"""
Pom: represents a Maven pom.xml file that can be modified
"""

import re
import xml.etree.ElementTree as ET
import logging
from typing import List, Optional

from mavengitupgrader.cxml import CommentedTreeBuilder


nsp = 'm'
nsu = "http://maven.apache.org/POM/4.0.0"
NSM = f"{{{nsu}}}"
NS = {nsp: nsu}
M = nsp + ':'
ET.register_namespace('', nsu)


class Dependency:
    def __init__(self, dependency_xml: ET.Element, properties_xml: ET.Element):
        group_xml = dependency_xml.find(M+"groupId", NS)
        if group_xml is None:
            logging.warning("Dependency group XML should not be None!")
        self.group: str = group_xml.text
        self.artifact: str = dependency_xml.find(M+"artifactId", NS).text
        self._version_xml: Optional[ET.Element] = \
            dependency_xml.find(M+"version", NS)
        if self._version_xml.text.startswith("${"):
            self.prop_name = re.findall(r'\${([^}]+)}', self._version_xml.text)[0]
            self._version_xml = properties_xml.find(M + self.prop_name, NS)
        else:
            self.prop_name = None

    def get_version(self):
        return self._version_xml.text

    def set_version(self, version_number: str):
        self._version_xml.text = str(version_number)


class Pom:
    def __init__(self, filename="pom.xml"):
        parser = ET.XMLParser(target=CommentedTreeBuilder())
        self.xml_tree = ET.parse(filename, parser)
        self.project = self.xml_tree.getroot()
        self._dependencies_xml = self.project.find(M+"dependencies", NS)
        self._properties_xml = self.project.find(M+"properties", NS)
        self.dependencies: List[Dependency] = list(map(
            lambda d: Dependency(d, self._properties_xml),
            filter(lambda x: x.tag == NSM+"dependency",
                   self._dependencies_xml)))

    def get_dependency(self, artifact_id: str,
                       group_id: str = None,
                       version: str = None):
        dep_list = self.dependencies
        dep_list = filter(lambda d: d.artifact == artifact_id, dep_list)
        if group_id:
            dep_list = filter(lambda d: d.group == group_id, dep_list)
        if version:
            dep_list = filter(lambda d: d.get_version() == version, dep_list)
        dep_list = list(dep_list)
        if dep_list:
            return dep_list[0]
        else:
            logging.warning("Pom.get_dependency(%s, %s, %s) found no matching"
                            " dependency and is returning None",
                            artifact_id, group_id, version)
            return None

    def save(self, filename: str):
        xml_str = ET.tostring(self.project, encoding='unicode')
        project_tag_too_wide = \
            '<project xmlns="http://maven.apache.org/POM/4.0.0"' \
            ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"' \
            ' xsi:schemaLocation="http://maven.apache.org/POM/4.0.0' \
            ' http://maven.apache.org/maven-v4_0_0.xsd">'
        project_tag_two_lines = \
            '<project xmlns="http://maven.apache.org/POM/4.0.0"' \
            ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n' \
            '         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0' \
            ' http://maven.apache.org/maven-v4_0_0.xsd">'
        if xml_str.startswith(project_tag_too_wide):
            xml_str = xml_str.replace(project_tag_too_wide,
                                      project_tag_two_lines, 1)
        if not xml_str.endswith('\n'):
            xml_str += '\n'
        logging.info("Saving pom file as %s", filename)
        with open(filename, 'w') as output:
            output.write(xml_str)
