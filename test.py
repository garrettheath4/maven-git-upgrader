import os.path
import subprocess
import unittest

from git import Branch
from maven import Pom
from update import Update


class FileHelper:
    # for TestBranch
    git_dir = "tmp"
    git_branch = "update-" + git_dir
    git_branch_b = git_branch + "-a"
    pom_filename = "pom-unittest-in.xml"
    pom_path_in_git = git_dir + "/" + pom_filename
    pom_update_contents_a = "Updated\nin\nnew\nbranch A.\n"
    pom_update_contents_b = "Updated\nin\nnew\nbranch B.\n"

    # for TestUpdate
    classgraph_update_line = "[INFO]   io.github.classgraph:classgraph " \
                             "..................... 4.8.71 -> 4.8.75"

    @staticmethod
    def assert_files_equal(filename_a: str, filename_b: str,
                           test_case: unittest.TestCase):
        with open(filename_a, 'r') as file_a, open(filename_b, 'r') as file_b:
            a_curr = "\n"
            b_curr = a_curr
            num_lines = 0
            while a_curr and b_curr:
                a_curr = file_a.readline()
                b_curr = file_b.readline()
                num_lines += 1
                test_case.assertEqual(a_curr, b_curr)
            test_case.assertEqual(a_curr, b_curr)
            test_case.assertGreater(num_lines, 1)

    @staticmethod
    def assert_files_not_equal(filename_a: str, filename_b: str,
                               test_case: unittest.TestCase):
        with open(filename_a, 'r') as file_a, open(filename_b, 'r') as file_b:
            a_curr = "\n"
            b_curr = a_curr
            while a_curr and b_curr:
                a_curr = file_a.readline()
                b_curr = file_b.readline()
                if a_curr != b_curr:
                    return
            test_case.fail(
                f"{filename_a} and {filename_b} have the same contents")

    @staticmethod
    def setup_branch_repo(test_case: unittest.TestCase) -> Branch:
        test_case.assertFalse("/" in FileHelper.git_dir
                              or "." in FileHelper.git_dir)
        cwd1 = subprocess.run(
            ['pwd'], check=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
        test_case.assertTrue(str(cwd1))
        branch = Branch(FileHelper.git_branch, based_on="master",
                        _git_dir_to_make=FileHelper.git_dir,
                        _pom_filename_to_copy=FileHelper.pom_filename)
        cwd2 = subprocess.run(
            ['pwd'], check=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
        test_case.assertEqual(cwd1, cwd2)
        test_case.assertTrue(os.path.isdir(FileHelper.git_dir))
        test_case.assertTrue(os.path.isdir(FileHelper.git_dir + "/.git"))
        test_case.assertTrue(os.path.isfile(FileHelper.pom_path_in_git))
        return branch

    @staticmethod
    def setup_update_repo(test_case: unittest.TestCase) -> Update:
        test_case.assertFalse("/" in FileHelper.git_dir
                              or "." in FileHelper.git_dir)
        cwd1 = subprocess.run(
            ['pwd'], check=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
        test_case.assertTrue(str(cwd1))
        update = Update(FileHelper.classgraph_update_line,
                        branch_to_update_from="master",
                        pom_filename=FileHelper.pom_filename,
                        _git_dir_to_make=FileHelper.git_dir,
                        _pom_filename_to_copy=FileHelper.pom_filename)
        cwd2 = subprocess.run(
            ['pwd'], check=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
        test_case.assertEqual(cwd1, cwd2)
        test_case.assertTrue(os.path.isdir(FileHelper.git_dir))
        test_case.assertTrue(os.path.isdir(FileHelper.git_dir + "/.git"))
        test_case.assertTrue(os.path.isfile(FileHelper.pom_path_in_git))
        return update

    @staticmethod
    def teardown():
        # check for uncommitted changes, just in case
        subprocess.run(['git', 'update-index', '--refresh'],
                       cwd=FileHelper.git_dir)
        subprocess.run(['git', 'diff-index', '--quiet', 'HEAD', '--'],
                       check=True, cwd=FileHelper.git_dir)
        subprocess.run(['rm',
                        FileHelper.git_dir + "/" + FileHelper.pom_filename],
                       check=True)
        subprocess.run(['rm', '-r', FileHelper.git_dir + "/.git"], check=True)
        subprocess.run(['rmdir', FileHelper.git_dir], check=True)


class TestMaven(unittest.TestCase):
    def test_pom(self):
        input_filename = "pom-unittest-in.xml"
        output_filename = "pom-unittest-out.xml"
        pom = Pom(input_filename)
        self.assertGreater(len(pom.dependencies), 0)
        pom.save(output_filename)
        self.assertTrue(os.path.isfile(output_filename))
        FileHelper.assert_files_equal(input_filename, output_filename, self)

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


class TestBranch(unittest.TestCase):
    def test_branch_mock_init(self):
        FileHelper.setup_branch_repo(self)
        FileHelper.teardown()

    def test_branch_mock_switch_to(self):
        branch = FileHelper.setup_branch_repo(self)
        old_branch = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stdout=subprocess.PIPE, check=True,
            cwd=FileHelper.git_dir).stdout.decode('utf-8').strip()
        self.assertEqual("master", old_branch)
        branch.activate()
        new_branch = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stdout=subprocess.PIPE, check=True,
            cwd=FileHelper.git_dir).stdout.decode('utf-8').strip()
        self.assertEqual(FileHelper.git_branch, new_branch)
        self.assertNotEqual(old_branch, new_branch)
        FileHelper.teardown()

    def test_branch_mock_switch_and_commit(self):
        FileHelper.setup_branch_repo(self).activate()
        with open(FileHelper.pom_path_in_git, 'w') as f:
            f.write(FileHelper.pom_update_contents_a)
        subprocess.run(['git', 'add', FileHelper.pom_filename],
                       check=True, cwd=FileHelper.git_dir)
        subprocess.run(['git', 'commit', '-m', "Update in Branch"],
                       check=True, cwd=FileHelper.git_dir)
        FileHelper.assert_files_not_equal(FileHelper.pom_filename,
                                          FileHelper.pom_path_in_git,
                                          self)
        subprocess.run(['git', 'checkout', 'master'],
                       check=True, cwd=FileHelper.git_dir)
        FileHelper.assert_files_equal(FileHelper.pom_filename,
                                      FileHelper.pom_path_in_git, self)
        FileHelper.teardown()

    def test_branch_mock_switch_commit_switch(self):
        branch_a = FileHelper.setup_branch_repo(self)
        branch_a.activate()
        with open(FileHelper.pom_path_in_git, 'w') as f:
            f.write(FileHelper.pom_update_contents_a)
        subprocess.run(['git', 'add', FileHelper.pom_filename],
                       check=True, cwd=FileHelper.git_dir)
        subprocess.run(['git', 'commit', '-m', "Update in Branch A"],
                       check=True, cwd=FileHelper.git_dir)
        branch_b = Branch(FileHelper.git_branch_b, based_on="master",
                          _git_dir_to_make=FileHelper.git_dir,
                          _pom_filename_to_copy=FileHelper.pom_filename)
        branch_b.activate()
        FileHelper.assert_files_equal(FileHelper.pom_filename,
                                      FileHelper.pom_path_in_git, self)
        with open(FileHelper.pom_path_in_git, 'w') as f:
            f.write(FileHelper.pom_update_contents_b)
        subprocess.run(['git', 'add', FileHelper.pom_filename],
                       check=True, cwd=FileHelper.git_dir)
        subprocess.run(['git', 'commit', '-m', "Update in Branch B"],
                       check=True, cwd=FileHelper.git_dir)
        FileHelper.assert_files_not_equal(FileHelper.pom_filename,
                                          FileHelper.pom_path_in_git, self)
        FileHelper.teardown()


class TestUpdate(unittest.TestCase):
    def test_update_line_classgraph(self):
        update = Update(FileHelper.classgraph_update_line,
                        pom_filename=FileHelper.pom_filename)
        self.assertTrue(update.parsed)
        self.assertEqual("io.github.classgraph", update.group)
        self.assertEqual("classgraph", update.artifact)
        self.assertEqual("4.8.71", update.current)
        self.assertEqual("4.8.75", update.latest)
        self.assertEqual("update-classgraph", update.branch.name)
        self.assertEqual("classgraph", update.pom_dependency.artifact)
        self.assertEqual("io.github.classgraph", update.pom_dependency.group)
        self.assertEqual("4.8.71", update.pom_dependency.get_version())


if __name__ == '__main__':
    unittest.main()
