import os
import unittest
import terraform_validate as t

class TestValidatorFunctional(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(os.path.dirname(os.path.realpath(__file__)))

    def test_resource(self):
        validator = t.Validator(os.path.join(self.path,"fixtures/resource"))
        validator.assert_resource_property_value_equals('aws_instance', 'value', 1)
        validator.resources('aws_instance').property('value').equals(1)
        self.assertRaises(AssertionError, validator.resources('aws_instance').property('value').equals,2)

    def test_nested_resource(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/nested_resource"))
        validator.assert_nested_resource_property_value_equals('aws_instance','nested_resource','value',1)
        validator.resources('aws_instance').property('nested_resource').property('value').equals(1)
        self.assertRaises(AssertionError, validator.resources('aws_instance').property('nested_resource').property('value').equals,2)

    def test_resource_not_equals(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/resource"))
        validator.assert_resource_property_value_not_equals('aws_instance', 'value', 0)
        validator.resources('aws_instance').property('value').not_equals(0)
        self.assertRaises(AssertionError, validator.resources('aws_instance').property('value').not_equals,1)

    def test_nested_resource_not_equals(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/nested_resource"))
        validator.assert_nested_resource_property_value_not_equals('aws_instance', 'nested_resource', 'value', 0)
        validator.resources('aws_instance').property('nested_resource').property('value').not_equals(0)
        self.assertRaises(AssertionError,validator.resources('aws_instance').property('nested_resource').property('value').not_equals,1)

    def test_resource_required_properties(self):
        required_properties = ['value', 'value2']
        validator = t.Validator(os.path.join(self.path, "fixtures/resource"))
        validator.assert_resource_has_properties('aws_instance', required_properties)
        validator.resources('aws_instance').has_properties(required_properties)
        required_properties = ['value', 'value2', 'abc123','def456']
        self.assertRaises(AssertionError, validator.resources('aws_instance').has_properties,required_properties)

    def test_nested_resource_required_properties(self):
        required_properties = ['value','value2']
        validator = t.Validator(os.path.join(self.path, "fixtures/nested_resource"))
        validator.assert_nested_resource_has_properties('aws_instance','nested_resource',required_properties)
        validator.resources('aws_instance').property('nested_resource').has_properties(required_properties)
        required_properties = ['value', 'value2', 'abc123', 'def456']
        self.assertRaises(AssertionError, validator.resources('aws_instance').property('nested_resource').has_properties,required_properties)

    def test_resource_property_value_matches_regex(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/resource"))
        validator.assert_resource_property_value_matches_regex('aws_instance',"value",'[0-9]')
        validator.resources('aws_instance').property('value').matches_regex('[0-9]')
        self.assertRaises(AssertionError, validator.resources('aws_instance').property('value').matches_regex,'[a-z]')

    def test_nested_resource_property_value_matches_regex(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/nested_resource"))
        validator.assert_nested_resource_property_value_matches_regex('aws_instance','nested_resource',"value",'[0-9]')
        validator.resources('aws_instance').property('nested_resource').property('value').matches_regex('[0-9]')
        self.assertRaises(AssertionError, validator.resources('aws_instance').property('nested_resource').property('value').matches_regex,'[a-z]')

    def test_variable_substitution(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/variable_substitution"))
        validator.enable_variable_expansion()
        validator.assert_resource_property_value_equals('aws_instance','value',1)
        validator.resources('aws_instance').property('value').equals(1)
        self.assertRaises(AssertionError,validator.resources('aws_instance').property('value').equals,2)

    def test_missing_variable_substitution(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/missing_variable"))
        validator.enable_variable_expansion()
        self.assertRaises(t.TerraformVariableException, validator.assert_resource_property_value_equals, 'aws_instance',
                          'value', 1)

        self.assertRaises(t.TerraformVariableException, validator.resources('aws_instance').property('value').equals,1)

    # def test_missing_required_nested_resource_fails(self):
    #     validator = t.Validator(os.path.join(self.path, "fixtures/resource"))
    #     self.assertRaises(AssertionError,validator.assert_nested_resource_property_value_equals,'aws_instance', 'tags', 'encrypted', 1)
    #     self.assertRaises(AssertionError,validator.resources('aws_instance').property('tags').property('encrypted').equals(1))

    def test_properties_on_nonexistant_resource_type(self):
        required_properties = ['value', 'value2']
        validator = t.Validator(os.path.join(self.path, "fixtures/missing_variable"))
        validator.assert_nested_resource_has_properties('aws_rds_instance', 'nested_resource', required_properties)
        validator.resources('aws_rds_instance').property('nested_resource').has_properties(required_properties)

    def test_searching_for_property_value_using_regex(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/regex_variables"))
        validator.assert_resource_regexproperty_value_equals('aws_instance', '^CPM_Service_[A-Za-z]+$', 1)
        validator.resources('aws_instance').find_property('^CPM_Service_[A-Za-z]+$').equals(1)
        self.assertRaises(AssertionError,validator.resources('aws_instance').find_property('^CPM_Service_[A-Za-z]+$').equals,2)

    def test_searching_for_nested_property_value_using_regex(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/regex_nested_variables"))
        validator.assert_nested_resource_regexproperty_value_equals('aws_instance', 'tags', '^CPM_Service_[A-Za-z]+$', 1)
        validator.resources('aws_instance').property('tags').find_property('^CPM_Service_[A-Za-z]+$').equals(1)
        self.assertRaises(AssertionError,validator.resources('aws_instance').property('tags').find_property('^CPM_Service_[A-Za-z]+$').equals,2)

    def test_resource_type_list(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/resource"))
        validator.assert_resource_property_value_equals(['aws_instance','aws_elb'], 'value', 1)
        validator.resources(['aws_instance','aws_elb']).property('value').equals(1)
        self.assertRaises(AssertionError,validator.resources(['aws_instance','aws_elb']).property('value').equals,2)

    def test_nested_resource_type_list(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/nested_resource"))
        validator.assert_nested_resource_property_value_equals(['aws_instance','aws_elb'],'tags', 'value', 1)
        validator.resources(['aws_instance', 'aws_elb']).property('tags').property('value').equals(1)
        validator.resources(['aws_instance', 'aws_elb']).property('tags').property('value')
        self.assertRaises(AssertionError,validator.resources(['aws_instance', 'aws_elb']).property('tags').property('value').equals,2)

    def test_invalid_terraform_syntax(self):
        self.assertRaises(t.TerraformSyntaxException, t.Validator,os.path.join(self.path, "fixtures/invalid_syntax"))

    def test_multiple_variable_substitutions(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/multiple_variables"))
        validator.enable_variable_expansion()
        validator.assert_resource_property_value_equals('aws_instance','value',12)
        validator.resources('aws_instance').property('value').equals(12)
        self.assertRaises(AssertionError,validator.resources('aws_instance').property('value').equals,21)

    def test_nested_multiple_variable_substitutions(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/multiple_variables"))
        validator.enable_variable_expansion()
        validator.assert_nested_resource_property_value_equals('aws_instance','value_block','value',21)
        validator.resources('aws_instance').property('value_block').property('value').equals(21)
        self.assertRaises(AssertionError,validator.resources('aws_instance').property('value_block').property('value').equals,12)

    def test_variable_expansion(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/variable_expansion"))
        validator.assert_resource_property_value_equals('aws_instance','value','${var.bar}')
        validator.resources('aws_instance').property('value').equals('${var.bar}')
        self.assertRaises(AssertionError,validator.resources('aws_instance').property('value').equals,'${bar.var}')

    def test_resource_name_matches_regex(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/resource_name"))
        validator.assert_resource_name_matches_regex('aws_foo', '^[a-z0-9_]*$')
        self.assertRaises(AssertionError,validator.assert_resource_name_matches_regex,'aws_instance','^[a-z0-9_]*$')
        validator.resources('aws_foo').name_matches_regex('^[a-z0-9_]*$')
        self.assertRaises(AssertionError,validator.resources('aws_instance').name_matches_regex,'^[a-z0-9_]*$')

    def test_variable_has_default_value(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/default_variable"))
        validator.assert_variable_default_value_exists('foo')
        self.assertRaises(AssertionError, validator.assert_variable_default_value_exists, 'bar')
        self.assertRaises(AssertionError, validator.variable('bar').default_value_exists)

    def test_variable_default_value_equals(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/default_variable"))
        validator.assert_variable_default_value_equals('foo',1)
        self.assertRaises(AssertionError, validator.assert_variable_default_value_equals, 'foo', 2)
        validator.assert_variable_default_value_equals('bar', None)

        self.assertRaises(AssertionError, validator.variable('bar').default_value_equals,2)
        validator.variable('bar').default_value_equals(None)

    def test_variable_default_value_matches_regex(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/default_variable"))
        validator.assert_variable_default_value_matches_regex('bizz', '^.*')
        self.assertRaises(AssertionError, validator.assert_variable_default_value_matches_regex, 'bizz', '^123')
        self.assertRaises(AssertionError, validator.variable('bizz').default_value_matches_regex, '^123')

    def test_no_exceptions_raised_when_no_resources_present(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/no_resources"))
        validator.assert_resource_property_value_equals('aws_instance', 'value', 1)
        validator.resources('aws_instance').property('value').equals(1)

    def test_lowercase_formatting_in_variable_substitution(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/lower_format_variable"))
        validator.enable_variable_expansion()
        validator.assert_resource_property_value_equals('aws_instance', 'value', "abc")
        validator.assert_resource_property_value_equals('aws_instance2', 'value', "abcDEF")

        validator.resources('aws_instance').property('value').equals('abc')
        validator.resources('aws_instance2').property('value').equals('abcDEF')

    def test_parsing_variable_with_unimplemented_interpolation_function(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/unimplemented_interpolation"))
        validator.enable_variable_expansion()
        self.assertRaises(t.TerraformUnimplementedInterpolationException,validator.assert_resource_property_value_equals, 'aws_instance', 'value', "abc")
        self.assertRaises(t.TerraformUnimplementedInterpolationException, validator.resources('aws_instance').property('value').equals,'abc')

    def test_encryption_scenario(self):
        validator = t.Validator(os.path.join(self.path, "fixtures/enforce_encrypted"))
        validator.error_if_property_missing()

        validator.resources("aws_db_instance_valid").property("storage_encrypted").equals("True")
        self.assertRaises(AssertionError, validator.resources("aws_db_instance_invalid").has_properties,"storage_encrypted")
        self.assertRaises(AssertionError, validator.resources("aws_db_instance_invalid").property("storage_encrypted").equals, "True")
        self.assertRaises(AssertionError, validator.resources("aws_db_instance_invalid2").property,"storage_encrypted")

        validator.resources("aws_instance_valid").property('ebs_block_device').property("encrypted").equals("True")
        self.assertRaises(AssertionError, validator.resources("aws_instance_invalid").has_properties, "encrypted")
        self.assertRaises(AssertionError, validator.resources("aws_instance_invalid").property('ebs_block_device').property("encrypted").equals, "True")
        self.assertRaises(AssertionError, validator.resources("aws_instance_invalid2").has_properties, "storage_encrypted")
        self.assertRaises(AssertionError, validator.resources("aws_instance_invalid2").property('ebs_block_device').property,"encrypted")

        validator.resources("aws_ebs_volume_valid").property("encrypted").equals("True")
        self.assertRaises(AssertionError, validator.resources("aws_ebs_volume_invalid").has_properties,"encrypted")
        self.assertRaises(AssertionError, validator.resources("aws_ebs_volume_invalid").property("encrypted").equals, "True")
        self.assertRaises(AssertionError, validator.resources("aws_ebs_volume_invalid2").has_properties, "encrypted")
        self.assertRaises(AssertionError, validator.resources("aws_ebs_volume_invalid2").property,"encrypted")


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestValidatorFunctional)
    unittest.TextTestRunner(verbosity=0).run(suite)
