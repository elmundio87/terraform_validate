import unittest
import terraform_validate as t

class TestValidatorNeoUnitHelper(unittest.TestCase):

    # def test_get_terraform_resource_that_exists(self):
    #     resources = {'resource': { 'aws_instance': {'foo': {'value2': 2, 'value': 1}, 'bar': {'value2': 2, 'value': 1}}}}
    #
    #     v = t.Validator(resources)
    #     a = v.resources('aws_instance')
    #     self.assertEqual(a.resource_list,[{'foo': {'value2': 2, 'value': 1}, 'bar': {'value2': 2, 'value': 1}}])
    #

    def test_get_terraform_resource_that_doesnt_exist(self):
        resources = {'resource': {'aws_instance': {'foo': {'value2': 2, 'value': 1}, 'bar': {'value2': 2, 'value': 1}}}}

        v = t.Validator(resources)
        a = v.resources('aws_rds')
        self.assertEqual(a.resources, [])

    def test_get_terraform_resource_that_doesnt_exist(self):
        resources = {'resource': {'aws_instance': {'foo': {'value2': 2, 'value': 1}, 'bar': {'value2': 2, 'value': 1}}}}

        v = t.Validator(resources)
        a = v.resources('aws_rds')
        self.assertEqual(a.resource_list, [])

    def test_get_terraform_property_that_exists(self):
        resources = {'resource': {'aws_instance': {'foo': {'value2': 2, 'value': 1}, 'bar': {'value2': 2, 'value': 1}}}}

        v = t.Validator(resources)
        v.resources('aws_instance').property('value').should_equal(1)
        self.assertRaises(AssertionError,  v.resources('aws_instance').property('value').should_equal,2)

    def test_get_all_resources(self):
        resources = {'resource': {'aws_instance': {'foo': {'value': 1}}, "aws_rds_instance": { 'bar': {'value': 1}}}}
        v = t.Validator(resources)
        a = v.resources(".*").property('value')
        self.assertEqual(len(a.properties),2)


    def test_get_all_aws_resources(self):
        resources = {'resource': {'aws_instance': {'foo': {'value': 1}}, "azure_rds_instance": {'bar': {'value': 1}}}}
        v = t.Validator(resources)
        a = v.resources("aws_.*").property('value')
        self.assertEqual(len(a.properties), 1)

class TestValidatorUnitHelper(unittest.TestCase):

    def test_get_terraform_resource_that_exists(self):
        resources = {"foo": {'value': 1}}
        v = t.Validator()
        a = v.get_terraform_resources('foo', resources)
        self.assertEqual(a, [{'value': 1}])

    def test_get_terraform_resource_that_doesnt_exist(self):
        resources = {"foo": {'value': 1}}
        v = t.Validator()
        a = v.get_terraform_resources('bar', resources)
        self.assertEqual(a, [])

    def test_matches_regex_is_true(self):
        v = t.Validator()
        a = v.matches_regex_pattern('abc_123', '^abc_123$')
        self.assertTrue(a)

    def test_matches_multiline_regex_is_true(self):
        v = t.Validator()
        a = v.matches_regex_pattern('abc_\n123', '^abc_.123$')
        self.assertTrue(a)

    def test_matches_regex_is_false(self):
        v = t.Validator()
        a = v.matches_regex_pattern('abc_123', '^abc_321$')
        self.assertFalse(a)

    def test_matches_regex_whole_string_only(self):
        v = t.Validator()
        a = v.matches_regex_pattern('abc_123', 'abc')
        self.assertFalse(a)

    def test_can_handle_no_variables_in_string(self):
        v = t.Validator()
        a = v.list_terraform_variables_in_string("wibble")
        self.assertEqual(a,[])

    def test_can_find_one_variable_in_string(self):
        v = t.Validator()
        a = v.list_terraform_variables_in_string("${var.abc}")
        self.assertEqual(a,["var.abc"])

    def test_can_find_multiple_variables_in_string(self):
        v = t.Validator()
        a = v.list_terraform_variables_in_string("${var.abc}${var.def}")
        self.assertEqual(a,["var.abc","var.def"])

    def test_can_find_multiple_variables_in_complex_string(self):
        v = t.Validator()
        a = v.list_terraform_variables_in_string("a${var.abc}b${var.def}c")
        self.assertEqual(a,["var.abc","var.def"])

    def test_handle_finding_variables_in_non_string_object(self):
        v = t.Validator()
        a = v.list_terraform_variables_in_string(1)
        self.assertEqual(a, [])

    def test_bool_to_str(self):
        a = t.TerraformPropertyList(None)
        self.assertEqual(t.TerraformPropertyList.bool2str(a,True),"True")
        self.assertEqual(t.TerraformPropertyList.bool2str(a, "True"), "True")
        self.assertEqual(t.TerraformPropertyList.bool2str(a, False), "False")
        self.assertEqual(t.TerraformPropertyList.bool2str(a, "False"), "False")


class TestTerraformVariableParser(unittest.TestCase):

    def test_simple_parse(self):
        a = t.TerraformVariableParser("var.lol")
        a.parse()
        self.assertEqual(a.variable, 'lol')

    def test_function_parse(self):
        a = t.TerraformVariableParser("lower(upper(var.lol))")
        a.parse()
        self.assertEqual(a.variable, 'lol')
        self.assertEqual(a.functions, ['lower','upper'])
