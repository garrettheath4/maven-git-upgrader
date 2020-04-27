import os.path
import subprocess
import unittest

from git import Branch
from maven import Pom
from update import Update


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
        self.assertEqual(new_version, dep2.get_version())
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


class TestUpdate(unittest.TestCase):
    def test_update_line_classgraph(self):
        update_line = "[INFO]   io.github.classgraph:classgraph" \
                      " ..................... 4.8.71 -> 4.8.75"
        update = Update(update_line, "pom-unittest-in.xml")
        self.assertTrue(update.parsed)
        self.assertEqual("io.github.classgraph", update.group)
        self.assertEqual("classgraph", update.artifact)
        self.assertEqual("4.8.71", update.current)
        self.assertEqual("4.8.75", update.latest)
        self.assertEqual("update-classgraph", update.branch.name)
        self.assertEqual("classgraph", update.pom_dependency.artifact)
        self.assertEqual("io.github.classgraph", update.pom_dependency.group)
        self.assertEqual("4.8.71", update.pom_dependency.get_version())


class TestBranch(unittest.TestCase):
    git_dir = "unittest"
    git_branch = "update-" + git_dir
    pom_filename = "pom-unittest-in.xml"

    def _setup_branch_repo(self) -> Branch:
        self.assertFalse(TestBranch.git_dir.startswith("/"))
        cwd1 = subprocess.run(
            ['pwd'], check=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
        self.assertTrue(str(cwd1))
        branch = Branch(TestBranch.git_branch,
                        TestBranch.git_dir, TestBranch.pom_filename)
        cwd2 = subprocess.run(
            ['pwd'], check=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
        self.assertEqual(cwd1, cwd2)
        self.assertTrue(os.path.isdir(TestBranch.git_dir))
        self.assertTrue(os.path.isdir(TestBranch.git_dir + "/.git"))
        return branch

    def test_branch_mock_init(self):
        self._setup_branch_repo()
        self._teardown()

    def test_branch_mock_switch_to(self):
        branch = self._setup_branch_repo()
        old_branch = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stdout=subprocess.PIPE, check=True,
            cwd=TestBranch.git_dir).stdout.decode('utf-8').strip()
        self.assertEqual("master", old_branch)
        branch.switch_to()
        new_branch = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stdout=subprocess.PIPE, check=True,
            cwd=TestBranch.git_dir).stdout.decode('utf-8').strip()
        self.assertEqual(TestBranch.git_branch, new_branch)
        self.assertNotEqual(old_branch, new_branch)
        self._teardown()

    # TODO: test_branch_mock_switch_to_TWO

    def _teardown(self):
        subprocess.run(['rm',
                        TestBranch.git_dir + "/" + TestBranch.pom_filename],
                       check=True)
        subprocess.run(['rm', '-r', TestBranch.git_dir + "/.git"], check=True)
        subprocess.run(['rmdir', TestBranch.git_dir], check=True)


if __name__ == '__main__':
    unittest.main()
