import unittest
import terraform_validate

class TestValidatorUnit(unittest.TestCase):

    def test_resource_property_value_equals_expected_value(self):
        v = terraform_validate.Validator()
        a = v.resource_property_value_equals("foo",{u'value':1},'aws_instance','value',1)
        self.assertEqual(a,None)

    def test_resource_property_value_equals_unexpected_value(self):
        v = terraform_validate.Validator()
        a = v.resource_property_value_equals("foo",{u'value':1},'aws_instance','value',2)
        self.assertEqual(len(a),1)
        self.assertEqual(a[0],"[aws_instance.foo.value] should be '2'. Is: '1'")


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEncryptionAtRest)
    unittest.TextTestRunner(verbosity=0).run(suite)
