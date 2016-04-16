import sys
import os
import unittest
#sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
import terraform_validate as t

class TestEncryptionAtRest(unittest.TestCase):
    def setUp(self):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"fixtures/1")
        self.terraform_config = terraform_validate.parse_terraform_directory(path)

    def test_instance_ebs_block_device(self):
        t.assert_nested_resource_property_value_equals(self.terraform_config,'foo','bizz','buzz',3)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEncryptionAtRest)
    unittest.TextTestRunner(verbosity=0).run(suite)
