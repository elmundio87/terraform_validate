import os
import unittest
import terraform_validate as t

class TestValidatorFunctional(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(os.path.dirname(os.path.realpath(__file__)))

    def test_resource(self):
        validator = t.Validator(os.path.join(self.path,"fixtures/resource"))
        validator.assert_resource_property_value_equals('aws_instance', 'value', 1)

    def test_nested_resource(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/nested_resource"))
        validator.assert_nested_resource_property_value_equals('aws_instance','nested_resource','value',1)

    def test_resource_not_equals(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/resource"))
        validator.assert_resource_property_value_not_equals('aws_instance', 'value', 0)

    def test_nested_resource_not_equals(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/nested_resource"))
        validator.assert_nested_resource_property_value_not_equals('aws_instance', 'nested_resource', 'value', 0)

    def test_resource_required_properties(self):
        required_properties = ['value', 'value2']
        validator = t.Validator(os.path.join(self.path, "fixtures/resource"))
        validator.assert_resource_has_properties('aws_instance', required_properties)

    def test_nested_resource_required_properties(self):
        required_properties = ['value','value2']
        validator = t.Validator(os.path.join(self.path, "fixtures/nested_resource"))
        validator.assert_nested_resource_has_properties('aws_instance','nested_resource',required_properties)

    def test_resource_property_value_matches_regex(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/resource"))
        validator.assert_resource_property_value_matches_regex('aws_instance',"value",'[0-9]')

    def test_nested_resource_property_value_matches_regex(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/nested_resource"))
        validator.assert_nested_resource_property_value_matches_regex('aws_instance','nested_resource',"value",'[0-9]')

    def test_nonexistant_nested_resource_property_value_matches_regex_fails(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/nested_resource"))
        try:
            validator.assert_nested_resource_property_value_matches_regex('aws_instance', 'nested_resource', "value3", '[0-9]')
            self.fail() #Fail if the above code passes
        except AssertionError:
            print("")

    def test_variable_substitution(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/variable_substitution"))
        validator.assert_resource_property_value_equals('aws_instance','value',1)

    def test_missing_variable_substitution(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/missing_variable"))
        try:
            validator.assert_resource_property_value_equals('aws_instance','value',1)
            self.fail() #Fail if the above code passes
        except t.TerraformVariableException:
            print("")

        validator = t.Validator(os.path.join(self.path, "fixtures/no_variables"))
        try:
            validator.assert_resource_property_value_equals('aws_instance','value',1)
            self.fail() #Fail if the above code passes
        except t.TerraformVariableException:
            print("")

    def test_properties_on_nonexistant_resource_type(self):
        required_properties = ['value', 'value2']
        validator = t.Validator(os.path.join(self.path, "fixtures/missing_variable"))
        validator.assert_nested_resource_has_properties('aws_rds_instance', 'nested_resource', required_properties)

    def test_searching_for_property_value_using_regex(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/regex_variables"))
        validator.assert_resource_regexproperty_value_equals('aws_instance', '^CPM_Service_[A-Za-z]+$', 1)

    def test_searching_for_nested_property_value_using_regex(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/regex_nested_variables"))
        validator.assert_nested_resource_regexproperty_value_equals('aws_instance', 'tags', '^CPM_Service_[A-Za-z]+$', 1)



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestValidatorFunctional)
    unittest.TextTestRunner(verbosity=0).run(suite)
