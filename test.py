import logging
import os.path
import unittest

from maven import Pom


logging.basicConfig(level="DEBUG")
log = logging.getLogger("test")


class TestMaven(unittest.TestCase):
    def test_pom(self):
        input_filename = "pom-unittest-in.xml"
        output_filename = "pom-unittest-out.xml"
        pom = Pom(input_filename)
        self.assertGreater(len(pom.dependencies), 0)
        pom.save(output_filename)
        self.assertTrue(os.path.isfile(output_filename))
        with open(input_filename, 'r') as i, open(output_filename, 'r') as o:
            i_curr = "\n"
            o_curr = i_curr
            num_lines = 0
            while i_curr and o_curr:
                i_curr = i.readline()
                o_curr = o.readline()
                num_lines += 1
                self.assertEqual(i_curr, o_curr)
            log.debug("number of lines checked: " + str(num_lines))
            self.assertGreater(num_lines, 1)

    def test_set_version(self):
        input_filename = "pom-unittest-in.xml"
        output_filename = "pom-unittest-out.xml"
        new_version = "9.9.9"
        pom = Pom(input_filename)
        self.assertGreater(len(pom.dependencies), 0)
        artifact = "scalatest_2.11"
        artifact_tag = f"<artifactId>{artifact}</artifactId>"
        scalatest_dep_list = list(filter(
            lambda d: d.artifact == artifact, pom.dependencies))
        self.assertEqual(len(scalatest_dep_list), 1)
        scalatest_dep_list[0].set_version(new_version)
        pom.save(output_filename)
        self.assertTrue(os.path.isfile(output_filename))
        with open(input_filename, 'r') as i, open(output_filename, 'r') as o:
            i_curr = "\n"
            o_curr = i_curr
            next_line_is_updated_version = False
            num_lines = 0
            while i_curr and o_curr:
                i_curr = i.readline()
                o_curr = o.readline()
                num_lines += 1
                if next_line_is_updated_version:
                    self.assertIn(new_version, o_curr)
                    self.assertNotIn(new_version, i_curr)
                    self.assertNotEqual(i_curr, o_curr)
                    next_line_is_updated_version = False
                else:
                    if artifact_tag in o_curr:
                        next_line_is_updated_version = True
                    self.assertEqual(i_curr, o_curr)
            log.debug("number of lines checked: " + str(num_lines))
            self.assertGreater(num_lines, 1)


if __name__ == '__main__':
    unittest.main()
