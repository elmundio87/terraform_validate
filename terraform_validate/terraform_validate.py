import hcl
import os
import re

class TerraformVariableException(Exception):
    pass

class Validator:

    def __init__(self,path):
        self.terraform_config = self.parse_terraform_directory(path)

    def parse_terraform_directory(self,path):

        terraform_string = ""
        for directory, subdirectories, files in os.walk(path):
            for file in files:
                if (file.endswith(".tf")):
                    with open(os.path.join(directory, file)) as fp:
                        terraform_string += fp.read()

        terraform = hcl.loads(terraform_string)
        return terraform

    def get_terraform_resources(self, name, resources):
        if name not in resources.keys():
            return []
        return resources[name]

    def matches_regex_pattern(self,variable, regex):
        return not (self.get_regex_matches(regex, variable) is None)

    def get_regex_matches(self, regex, variable):
        p = re.compile(regex)
        return p.match(str(variable))

    def is_terraform_variable(self, variable):
        return self.matches_regex_pattern(variable,'\${var.(.*)}')

    def get_terraform_variable_name(self, s):
        return self.get_regex_matches('\${var.(.*)}', s).group(1)

    def get_terraform_variable_value(self,variable):
        if ('variable' not in self.terraform_config.keys()) or (variable not in self.terraform_config['variable'].keys()):
            raise TerraformVariableException("There is no Terraform variable '{0}'".format(variable))
        if 'default' not in self.terraform_config['variable'][variable].keys():
            return None
        return self.terraform_config['variable'][variable]['default']

    def get_terraform_properties_that_match_regex(self,regex,properties):
        out = {}
        for property in properties:
            if self.matches_regex_pattern(property,regex):
                out[property] = properties[property]

        return out

    def get_terraform_property_value(self, name,values):

        if name not in values:
            return None
        for value in values:
            if self.is_terraform_variable(values[value]):
                values[value] = self.get_terraform_variable_value(self.get_terraform_variable_name(values[value]))
        return values[name]

    def convert_to_list(self, nested_resources):
        if not type(nested_resources) == list:
            nested_resources = [nested_resources]
        return nested_resources

    def assert_resource_base(self, resource_type, closure):
        errors = []
        resources = self.get_terraform_resources(resource_type, self.terraform_config['resource'])
        for resource in resources:
            error = closure(resource,resources[resource])
            if error is not None: errors += error
        if len(errors) > 0:
            raise AssertionError("\n".join(errors))

    def assert_nested_resource_base(self, resource_type, nested_resource_name, closure):
        errors = []
        resources = self.get_terraform_resources(resource_type, self.terraform_config['resource'])
        for resource in resources:
            nested_resources = self.convert_to_list(self.get_terraform_resources(nested_resource_name, resources[resource]))
            for nested_resource in nested_resources:
                error = closure(resource,nested_resource)
                if error is not None: errors += error
        if len(errors) > 0:
            raise AssertionError("\n".join(errors))

    def assert_resource_property_value_equals(self, resource_type, property, property_value):

        def closure(resource_name, resource):
            calculated_property_value = self.get_terraform_property_value(property,resource)
            if not (str(calculated_property_value) == str(property_value)):
                return ["[{0}.{1}.{2}] should be '{3}'. Is: '{4}'".format(resource_type, resource_name, property, property_value, calculated_property_value)]

        self.assert_resource_base(resource_type, closure)

    def assert_resource_has_properties(self,resource_type,required_properties):

        def closure(resource_name,resource):
            errors = []
            property_names = resource.keys()
            for required_property_name in required_properties:
                if not required_property_name in property_names:
                    errors += ["[{0}.{1}] should have property: '{2}'".format(resource_type,resource_name, required_property_name)]
            return errors
        self.assert_resource_base(resource_type, closure)

    def assert_resource_property_value_matches_regex(self, resource_type, property, regex):

        def closure(resource_name,resource):
                calculated_property_value = self.get_terraform_property_value(property, resource)
                if not self.matches_regex_pattern(str(calculated_property_value),regex):
                    return ["[{0}.{1}.{2}] should match regex '{3}'. Is: '{4}'".format(resource_type, resource_name, property, regex, calculated_property_value)]

        self.assert_resource_base(resource_type, closure)

    def assert_resource_regexproperty_value_equals(self, resource_type, regex, property_value):
        def closure(resource_name,resource):
            properties = self.get_terraform_properties_that_match_regex(regex, resource)

            if len(properties.keys()) == 0:
                return ["[{0}.{1}] No properties were found that match the regex '{3}'".format(resource_type, resource, regex)]

            for property in properties.keys():
                calculated_property_value = self.get_terraform_property_value(property, resource)
                if not (str(calculated_property_value) == str(property_value)):
                    return ["[{0}.{1}.{2}] should be '{3}'. Is: '{4}'".format(resource_type, resource_name, property, property_value, calculated_property_value)]

        self.assert_resource_base(resource_type, closure)

    def assert_nested_resource_has_properties(self, resource_type, nested_resource_name, required_properties):

        def closure(resource_name, nested_resource):
            errors = []
            property_names = nested_resource.keys()
            for required_property_name in required_properties:
                if not required_property_name in property_names:
                    errors += ["[{0}.{1}.{2}] should have property: '{3}'".format(resource_type, resource_name, nested_resource_name, required_property_name)]
            return errors
        self.assert_nested_resource_base(resource_type, nested_resource_name, closure)

    def assert_nested_resource_property_value_matches_regex(self, resource_type, nested_resource_name, property, regex):

        def closure(resource_name, nested_resource):
            calculated_property_value = self.get_terraform_property_value(property, nested_resource)
            if not self.matches_regex_pattern(str(calculated_property_value), regex):
                return [
                    "[{0}.{1}.{2}.{3}] should match regex '{4}'. Is: '{5}'".format(resource_type, resource_name, nested_resource_name, property, regex, calculated_property_value)]

        self.assert_nested_resource_base(resource_type, nested_resource_name, closure)

    def assert_nested_resource_property_value_equals(self, resource_type, nested_resource_name, property, property_value):

        def closure(resource_name, nested_resource):
            calculated_property_value = self.get_terraform_property_value(property, nested_resource)
            if not (str(calculated_property_value) == str(property_value)):
                return ["[{0}.{1}.{2}.{3}] should be '{4}'. Is: '{5}'".format(resource_type, resource_name, nested_resource_name, property, property_value, calculated_property_value)]

        self.assert_nested_resource_base(resource_type, nested_resource_name, closure)


    def assert_nested_resource_regexproperty_value_equals(self, resource_type, nested_resource_name, regex, property_value):
        def closure(resource_name, nested_resource):
            properties = self.get_terraform_properties_that_match_regex(regex,nested_resource)

            if len(properties.keys()) == 0:
                return["[{0}.{1}.{2}] No properties were found that match the regex '{3}'".format(resource_type, resource_name, nested_resource_name, regex)]

            for property in properties.keys():
                calculated_property_value = self.get_terraform_property_value(property, nested_resource)
                if not (str(calculated_property_value) == str(property_value)):
                    return ["[{0}.{1}.{2}.{3}] should be '{4}'. Is: '{5}'".format(resource_type, resource_name, nested_resource_name, property, property_value, calculated_property_value)]

        self.assert_nested_resource_base(resource_type, nested_resource_name, closure)