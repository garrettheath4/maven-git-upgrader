"""
Pom: represents a Maven pom.xml file that can be modified
"""

import re
import xml.etree.ElementTree as ET
import logging

from cxml import CommentedTreeBuilder

logging.basicConfig(level="DEBUG")
log = logging.getLogger("maven")


nsp = 'm'
nsu = "http://maven.apache.org/POM/4.0.0"
NS = {nsp: nsu}
M = nsp + ':'
ET.register_namespace('', nsu)


class Dependency:
    def __init__(self, dependency_xml: ET.Element, properties_xml: ET.Element):
        self.group = dependency_xml.find(M+"groupId", NS).text
        self.artifact = dependency_xml.find(M+"artifactId", NS).text
        self.version_xml = dependency_xml.find(M+"version", NS)
        if self.version_xml.text.startswith("${"):
            prop_name = re.findall(r'\$\{([^}]+)\}', self.version_xml.text)[0][0]
            self.version_xml = properties_xml.find(M+prop_name, NS)


class Pom:
    def __init__(self, filename="pom.xml"):
        parser = ET.XMLParser(target=CommentedTreeBuilder())
        self.xml_tree = ET.parse(filename, parser)
        self.project = self.xml_tree.getroot()
        log.debug(self.project)
        self.dependencies_xml = self.project.find(M+"dependencies", NS)
        log.debug(self.dependencies_xml)
        self.properties_xml = self.project.find(M+"properties", NS)
        self.dependencies = map(lambda d: Dependency(d, self.properties_xml),
                                self.dependencies_xml)

    def save(self, filename: str):
        xml_str = ET.tostring(self.project, encoding='unicode')
        log.debug(type(xml_str))
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
            log.debug("startswith == true")
            xml_str = xml_str.replace(project_tag_too_wide, project_tag_two_lines, 1)
        else:
            log.debug("startswith == false")
        if not xml_str.endswith('\n'):
            xml_str += '\n'
        log.debug(xml_str[0:220])
        with open(filename, 'w') as output:
            output.write(xml_str)
