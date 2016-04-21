import unittest
import terraform_validate

class TestValidatorUnit(unittest.TestCase):

    def test_resource_property_value_equals_expected_value(self):
        v = terraform_validate.Validator()
        a = v.resource_property_value_equals("foo",{u'value':1},'aws_instance','value',1)
        self.assertEqual(a,[])

    def test_resource_property_value_equals_unexpected_value(self):
        v = terraform_validate.Validator()
        a = v.resource_property_value_equals("foo",{u'value':1},'aws_instance','value',2)
        self.assertEqual(len(a),1)
        self.assertEqual(a[0],"[aws_instance.foo.value] should be '2'. Is: '1'")

    def test_resource_has_properties_expected_values(self):
        v = terraform_validate.Validator()
        a = v.resource_has_properties("foo",{u'value1':1,u'value2':2},'aws_instance',['value1','value2'])
        self.assertEqual(a,[])

    def test_resource_has_properties_expected_values_one_missing(self):
        v = terraform_validate.Validator()
        a = v.resource_has_properties("foo", {u'value1': 1, u'value2': 2}, 'aws_instance', ['value1', 'value2','value3'])
        self.assertEqual(a, ["[aws_instance.foo] should have property: 'value3'"])

    def test_resource_has_properties_expected_values_two_missing(self):
        v = terraform_validate.Validator()
        a = v.resource_has_properties("foo", {u'value1': 1, u'value2': 2}, 'aws_instance', ['value1', 'value2','value3','value4'])
        self.assertEqual(a, ["[aws_instance.foo] should have property: 'value3'",
                             "[aws_instance.foo] should have property: 'value4'"])

    def test_resource_value_matches_regex_expected_value(self):
        v = terraform_validate.Validator()
        a = v.resource_value_matches_regex("foo", {u'value': '1'}, 'aws_instance','value', '[0-9]')
        self.assertEqual(a, [])

    def test_resource_value_matches_regex_unexpected_value(self):
        v = terraform_validate.Validator()
        a = v.resource_value_matches_regex("foo", {u'value': 'a'}, 'aws_instance','value', '[0-9]')
        self.assertEqual(a, ["[aws_instance.foo.value] should match regex '[0-9]'. Is: 'a'"])


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEncryptionAtRest)
    unittest.TextTestRunner(verbosity=0).run(suite)
