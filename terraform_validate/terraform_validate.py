import hcl
import os
import re

class TerraformSyntaxException(Exception):
    pass

class TerraformVariableException(Exception):
    pass

class Validator:

    def __init__(self,path=None):
        self.variable_expand = True
        if path is not None:
            self.terraform_config = self.parse_terraform_directory(path)

    def disable_variable_expansion(self):
        self.variable_expand = False

    def parse_terraform_directory(self,path):

        terraform_string = ""
        for directory, subdirectories, files in os.walk(path):
            for file in files:
                if (file.endswith(".tf")):
                    with open(os.path.join(directory, file)) as fp:
                        new_terraform = fp.read()
                        try:
                            hcl.loads(new_terraform)
                        except ValueError as e:
                            raise TerraformSyntaxException("Invalid terraform configuration in {0}\n{1}".format(os.path.join(directory,file),e))
                        terraform_string += new_terraform
        terraform = hcl.loads(terraform_string)
        return terraform

    def get_terraform_resources(self, name, resources):
        if name not in resources.keys():
            return []
        return self.convert_to_list(resources[name])

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

    def substitute_variable_values_in_string(self, s):
        if not isinstance(s,dict):
            for variable in self.list_terraform_variables_in_string(s):
                variable_default_value = self.get_terraform_variable_value(variable)
                if variable_default_value != None:
                    s = s.replace('${var.'+variable+'}',variable_default_value)
        return s

    def list_terraform_variables_in_string(self, s):
        return re.findall('\${var.(\w+)}',str(s))

    def get_terraform_property_value(self, name,values):
        if name not in values:
            return None
        for value in values:
            if self.variable_expand:
                values[value] = self.substitute_variable_values_in_string(values[value])
        return values[name]

    def convert_to_list(self, nested_resources):
        if not type(nested_resources) == list:
            nested_resources = [nested_resources]
        return nested_resources

    def assert_variable_base(self, variable_name, closure):
        errors = []
        default_variable_value = self.get_terraform_variable_value(variable_name)
        error = closure(variable_name, default_variable_value)
        if error is not None: errors += error
        if len(errors) > 0:
            raise AssertionError("\n".join(errors))

    def assert_resource_base(self, resource_types, closure):
        errors = []
        resources = {}
        resource_types = self.convert_to_list(resource_types)
        for resource_type in resource_types:
            if resource_type not in resources.keys():
                resources[resource_type] = []
            if 'resource' in self.terraform_config.keys():
                resources[resource_type] += self.get_terraform_resources(resource_type, self.terraform_config['resource'])

        for resource_type in resource_types:
            for resource in resources[resource_type]:
                    for resource_name in resource.keys():
                        error = closure(resource_type, resource_name,resource[resource_name])
                    if error is not None: errors += error
        if len(errors) > 0:
            raise AssertionError("\n".join(errors))

    def assert_nested_resource_base(self, resource_types, nested_resource_name, closure):
        errors = []
        resources = {}
        resource_types = self.convert_to_list(resource_types)
        for resource_type in resource_types:
            if resource_type not in resources.keys():
                resources[resource_type] = []
            if 'resource' in self.terraform_config.keys():
                resources[resource_type] += self.get_terraform_resources(resource_type, self.terraform_config['resource'])

        for resource_type in resource_types:
            for resource in resources[resource_type]:
                for resource_name in resource.keys():
                    nested_resources = self.convert_to_list(self.get_terraform_resources(nested_resource_name, resource[resource_name]))
                    #if len(nested_resources) == 0:
                    #    errors += ["[{0}.{1}] is missing nested resource '{2}'".format(resource_type, resource_name, nested_resource_name)]
                    for nested_resource in nested_resources:
                        error = closure(resource_type, "{0}.{1}".format(resource_name,nested_resource_name),nested_resource)
                        if error is not None: errors += error
        if len(errors) > 0:
            raise AssertionError("\n".join(errors))

    def resource_property_value_equals(self, resource_name, resource, resource_type, property, property_value):
        calculated_property_value = self.get_terraform_property_value(property, resource)
        if not (str(calculated_property_value) == str(property_value)):
            return ["[{0}.{1}.{2}] should be '{3}'. Is: '{4}'".format(resource_type, resource_name, property, property_value, calculated_property_value)]
        return []

    def assert_resource_property_value_equals(self,resource_type,property,property_value):
        def closure(resource_type, resource_name, resource):
            return self.resource_property_value_equals(resource_name, resource, resource_type, property, property_value)
        self.assert_resource_base(resource_type, closure)

    def assert_nested_resource_property_value_equals(self, resource_type, nested_resource_name, property, property_value):
        def closure(resource_type, resource_name, resource):
            return self.resource_property_value_equals(resource_name, resource, resource_type, property, property_value)
        self.assert_nested_resource_base(resource_type, nested_resource_name, closure)

    def resource_property_value_not_equals(self, resource_name, resource, resource_type, property, property_value):
        calculated_property_value = self.get_terraform_property_value(property, resource)
        if (str(calculated_property_value) == str(property_value)):
            return ["[{0}.{1}.{2}] should not be '{3}'. Is: '{4}'".format(resource_type, resource_name, property, property_value, calculated_property_value)]
        return []

    def assert_resource_property_value_not_equals(self, resource_type, property, property_value):
        def closure(resource_type, resource_name, resource):
            return self.resource_property_value_not_equals(resource_name, resource, resource_type, property, property_value)
        self.assert_resource_base(resource_type, closure)

    def assert_nested_resource_property_value_not_equals(self, resource_type, nested_resource_name, property, property_value):
        def closure(resource_type, resource_name, resource):
            return self.resource_property_value_not_equals(resource_name, resource, resource_type, property, property_value)
        self.assert_nested_resource_base(resource_type, nested_resource_name, closure)

    def resource_has_properties(self,resource_name,resource,resource_type,required_properties):
        errors = []
        property_names = resource.keys()
        for required_property_name in required_properties:
            if not required_property_name in property_names:
                errors += ["[{0}.{1}] should have property: '{2}'".format(resource_type, resource_name, required_property_name)]
        return errors

    def assert_resource_has_properties(self,resource_type,required_properties):
        def closure(resource_type, resource_name,resource):
            return self.resource_has_properties(resource_name,resource,resource_type,required_properties)
        self.assert_resource_base(resource_type, closure)

    def assert_nested_resource_has_properties(self, resource_type, nested_resource_name, required_properties):
        def closure(resource_type, resource_name, resource):
            return self.resource_has_properties(resource_name, resource, resource_type, required_properties)
        self.assert_nested_resource_base(resource_type, nested_resource_name, closure)

    def resource_property_value_matches_regex(self,resource_name,resource,resource_type,property,regex):
        calculated_property_value = self.get_terraform_property_value(property, resource)
        if not self.matches_regex_pattern(str(calculated_property_value), regex):
            return ["[{0}.{1}.{2}] should match regex '{3}'. Is: '{4}'".format(resource_type, resource_name, property, regex, calculated_property_value)]
        return []

    def assert_resource_property_value_matches_regex(self, resource_type, property, regex):
        def closure(resource_type, resource_name,resource):
            return self.resource_property_value_matches_regex(resource_name, resource, resource_type, property, regex)
        self.assert_resource_base(resource_type, closure)

    def assert_nested_resource_property_value_matches_regex(self, resource_type, nested_resource_name, property, regex):
        def closure(resource_type, resource_name, resource):
            return self.resource_property_value_matches_regex(resource_name, resource, resource_type, property, regex)
        self.assert_nested_resource_base(resource_type, nested_resource_name, closure)

    def assert_resource_name_matches_regex(self, resource_type, regex):
        def closure(resource_type, resource_name, resource):
            if not self.matches_regex_pattern(resource_name, regex):
                return [
                    "[{0}.{1}] should match regex '{2}'".format(resource_type, resource_name, regex )]
            return []
        self.assert_resource_base(resource_type, closure)

    def resource_regexproperty_value_equals(self,resource_name,resource,resource_type,regex,property_value):
        properties = self.get_terraform_properties_that_match_regex(regex, resource)

        if len(properties.keys()) == 0:
            return ["[{0}.{1}] No properties were found that match the regex '{2}'".format(resource_type, resource_name, regex)]

        for property in properties.keys():
            calculated_property_value = self.get_terraform_property_value(property, resource)
            if not (str(calculated_property_value) == str(property_value)):
                return ["[{0}.{1}.{2}] should be '{3}'. Is: '{4}'".format(resource_type, resource_name, property, property_value, calculated_property_value)]
        return []

    def assert_resource_regexproperty_value_equals(self, resource_type, regex, property_value):
        def closure(resource_type, resource_name,resource):
            return self.resource_regexproperty_value_equals(resource_name,resource,resource_type,regex,property_value)
        self.assert_resource_base(resource_type, closure)

    def assert_nested_resource_regexproperty_value_equals(self, resource_type, nested_resource_name, regex, property_value):
        def closure(resource_type, resource_name, resource):
            return self.resource_regexproperty_value_equals(resource_name, resource, resource_type, regex, property_value)
        self.assert_nested_resource_base(resource_type, nested_resource_name, closure)

    def assert_variable_default_value_exists(self, variable_name):
        def closure(variable_name, default_variable_value):
            if default_variable_value == None:
                return ["Variable {0} should have a default value".format(variable_name)]
            return []
        self.assert_variable_base(variable_name, closure)

    def assert_variable_default_value_equals(self, variable_name, variable_value):
        def closure(variable_name, default_variable_value):
            if str(default_variable_value) != str(variable_value):
                return ["Variable {0} should have a default value of {1}. Is: {2}".format(variable_name, variable_value, default_variable_value)]
            return []
        self.assert_variable_base(variable_name, closure)

    def assert_variable_default_value_matches_regex(self, variable_name, regex):
        def closure(variable_name, default_variable_value):
            if not self.matches_regex_pattern(default_variable_value, regex):
                return [
                    "Variable {0} should have a default value that matches regex '{1}'. Is: {2}".format(variable_name, regex, default_variable_value)]
            return []
        self.assert_variable_base(variable_name, closure)









