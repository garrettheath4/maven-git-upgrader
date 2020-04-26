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


if __name__ == '__main__':
    unittest.main()
