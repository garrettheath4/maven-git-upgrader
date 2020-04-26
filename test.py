import os.path
import unittest

from maven import Pom


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
            self.assertGreaterEqual(num_lines, 9)

    def test_set_version_simple(self):
        input_filename = "pom-unittest-in.xml"
        output_filename = "pom-unittest-out.xml"
        new_version = "9.9.9"
        pom = Pom(input_filename)
        self.assertGreater(len(pom.dependencies), 0)
        artifact = "scalatest_2.11"
        artifact_tag = f"<artifactId>{artifact}</artifactId>"
        dep = pom.get_dependency(artifact)
        self.assertIsNotNone(dep)
        dep.set_version(new_version)
        pom.save(output_filename)
        self.assertTrue(os.path.isfile(output_filename))
        with open(input_filename, 'r') as i, open(output_filename, 'r') as o:
            i_curr = "\n"
            o_curr = i_curr
            found_updated_version = False
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
                    found_updated_version = True
                else:
                    if artifact_tag in o_curr:
                        next_line_is_updated_version = True
                    self.assertEqual(i_curr, o_curr)
            self.assertTrue(found_updated_version)
            self.assertGreaterEqual(num_lines, 9)

    def test_set_version_property_used_once(self):
        input_filename = "pom-unittest-in.xml"
        output_filename = "pom-unittest-out.xml"
        new_version = "8.8.8"
        pom = Pom(input_filename)
        self.assertGreater(len(pom.dependencies), 0)
        artifact = "scala-library"
        dep = pom.get_dependency(artifact)
        self.assertIsNotNone(dep)
        dep.set_version(new_version)
        prop_name = dep.prop_name
        version_prop_tag = f"<{prop_name}>"
        pom.save(output_filename)
        self.assertTrue(os.path.isfile(output_filename))
        with open(input_filename, 'r') as i, open(output_filename, 'r') as o:
            i_curr = "\n"
            o_curr = i_curr
            num_lines = 0
            found_version_prop_tag = False
            while i_curr and o_curr:
                i_curr = i.readline()
                o_curr = o.readline()
                num_lines += 1
                if version_prop_tag in o_curr:
                    found_version_prop_tag = True
                    self.assertIn(new_version, o_curr)
                    self.assertNotIn(new_version, i_curr)
                    self.assertNotEqual(i_curr, o_curr)
                else:
                    self.assertEqual(i_curr, o_curr)
            self.assertTrue(found_version_prop_tag)
            self.assertGreaterEqual(num_lines, 9)

    def test_set_version_property_used_twice(self):
        input_filename = "pom-unittest-in.xml"
        output_filename = "pom-unittest-out.xml"
        new_version = "7.7.7"
        pom = Pom(input_filename)
        self.assertGreater(len(pom.dependencies), 0)
        artifact1 = "logback-classic"
        artifact2 = "logback-core"
        dep1 = pom.get_dependency(artifact1)
        self.assertIsNotNone(dep1)
        dep1.set_version(new_version)
        dep2 = pom.get_dependency(artifact2)
        self.assertIsNotNone(dep2)
        self.assertEqual(new_version, dep2.version)
        prop_name = dep1.prop_name
        version_prop_tag = f"<{prop_name}>"
        pom.save(output_filename)
        self.assertTrue(os.path.isfile(output_filename))
        with open(input_filename, 'r') as i, open(output_filename, 'r') as o:
            i_curr = "\n"
            o_curr = i_curr
            num_lines = 0
            found_version_prop_tag = False
            while i_curr and o_curr:
                i_curr = i.readline()
                o_curr = o.readline()
                num_lines += 1
                if version_prop_tag in o_curr:
                    found_version_prop_tag = True
                    self.assertIn(new_version, o_curr)
                    self.assertNotIn(new_version, i_curr)
                    self.assertNotEqual(i_curr, o_curr)
                else:
                    self.assertEqual(i_curr, o_curr)
            self.assertTrue(found_version_prop_tag)
            self.assertGreaterEqual(num_lines, 9)


if __name__ == '__main__':
    unittest.main()
