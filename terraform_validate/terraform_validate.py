import hcl
import os
import re
import warnings

def deprecated(func):
    '''This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.'''
    def new_func(*args, **kwargs):
        print("The method '{0}' is deprecated as of v2.0. Please refer to the readme for the recommended usage of this library.".format(func.__name__))
        print("'{0}' will be removed in a future release.".format(func.__name__))
        return func(*args, **kwargs)
    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)
    return new_func


class TerraformSyntaxException(Exception):
    pass

class TerraformVariableException(Exception):
    pass

class TerraformUnimplementedInterpolationException(Exception):
    pass

class TerraformVariableParser:

    def __init__(self,string):
        self.string = string
        self.functions = []
        self.variable = ""
        self.state = 0
        self.index = 0

    def parse(self):
        while self.index < len(self.string):
            if self.state == 0:
                if self.string[self.index:self.index+3] == "var":
                    self.index += 3
                    self.state = 1
                else:
                    self.state = 3
                    temp_function = ""
            if self.state == 1:
                temp_var = ""
                while True:
                    self.index += 1
                    if self.index == len(self.string) or self.string[self.index] == ")":
                        self.variable = temp_var
                        self.state = 2
                        break;
                    else:
                        temp_var += self.string[self.index]
            if self.state == 2:
                self.index += 1
            if self.state == 3:
                if self.string[self.index] == "(":
                    self.state = 0
                    self.functions.append(temp_function)
                else:
                    temp_function += self.string[self.index]
                self.index += 1

class TerraformVariable:

    def default_value(self):
        return TerraformProperty()

class TerraformPropertyList:

    def __init__(self, validator):
        self.properties = []
        self.validator = validator

    def property(self, property_name):
        errors = []
        list = TerraformPropertyList(self.validator)
        for property in self.properties:
            if property_name in property.property_value.keys():
                list.properties.append(TerraformProperty(property.resource_type,
                                                     "{0}.{1}".format(property.resource_name,property.property_name),
                                                     property_name,
                                                     property.property_value[property_name]))
            elif self.validator.raise_error_if_property_missing:
                errors.append("[{0}.{1}] should have property: '{2}'".format(property.resource_type, "{0}.{1}".format(property.resource_name,property.property_name), property_name))

        if len(errors) > 0:
            raise AssertionError("\n".join(sorted(errors)))

        return list

    def should_equal(self,expected_value):
        errors = []
        for property in self.properties:

            actual_property_value = self.validator.substitute_variable_values_in_string(property.property_value)

            expected_value = self.int2str(expected_value)
            actual_property_value = self.int2str(actual_property_value)
            expected_value = self.bool2str(expected_value)
            actual_property_value = self.bool2str(actual_property_value)

            if actual_property_value != expected_value:
                errors.append("[{0}.{1}.{2}] should be '{3}'. Is: '{4}'".format(property.resource_type,
                                                                        property.resource_name,
                                                                        property.property_name,
                                                                        expected_value,
                                                                        actual_property_value))
        if len(errors) > 0:
            raise AssertionError("\n".join(sorted(errors)))

    def should_not_equal(self,expected_value):
        errors = []
        for property in self.properties:

            actual_property_value = self.validator.substitute_variable_values_in_string(property.property_value)

            actual_property_value = self.int2str(actual_property_value)
            expected_value = self.int2str(expected_value)
            expected_value = self.bool2str(expected_value)
            actual_property_value = self.bool2str(actual_property_value)

            if actual_property_value == expected_value:
                errors.append("[{0}.{1}.{2}] should not be '{3}'. Is: '{4}'".format(property.resource_type,
                                                                        property.resource_name,
                                                                        property.property_name,
                                                                        expected_value,
                                                                        actual_property_value))

        if len(errors) > 0:
            raise AssertionError("\n".join(sorted(errors)))

    def list_should_contain(self,values_list):
        errors = []

        if type(values_list) is not  list:
            values_list = [values_list]

        for property in self.properties:

            actual_property_value = self.validator.substitute_variable_values_in_string(property.property_value)
            values_missing = []
            for value in values_list:
                if value not in actual_property_value :
                    values_missing.append(value)

            if len(values_missing) != 0:
                if type(actual_property_value) is list:
                    actual_property_value = [str(x) for x in actual_property_value] # fix 2.6/7
                errors.append("[{0}.{1}.{2}] '{3}' should contain '{4}'.".format(property.resource_type,
                                                                        property.resource_name,
                                                                        property.property_name,
                                                                        actual_property_value,
                                                                        values_missing))
        if len(errors) > 0:
            raise AssertionError("\n".join(sorted(errors)))

    def list_should_not_contain(self,values_list):
        errors = []

        if type(values_list) is not  list:
            values_list = [values_list]

        for property in self.properties:

            actual_property_value = self.validator.substitute_variable_values_in_string(property.property_value)
            values_missing = []
            for value in values_list:
                if value in actual_property_value :
                    values_missing.append(value)

            if len(values_missing) != 0:
                if type(actual_property_value) is list:
                    actual_property_value = [str(x) for x in actual_property_value] # fix 2.6/7
                errors.append("[{0}.{1}.{2}] '{3}' should not contain '{4}'.".format(property.resource_type,
                                                                        property.resource_name,
                                                                        property.property_name,
                                                                        actual_property_value,
                                                                        values_missing))
        if len(errors) > 0:
            raise AssertionError("\n".join(sorted(errors)))


    def should_have_properties(self, properties_list):
        errors = []

        if type(properties_list) is not  list:
            properties_list = [properties_list]

        for property in self.properties:
            property_names = property.property_value.keys()
            for required_property_name in properties_list:
                if required_property_name not in property_names:
                    errors.append("[{0}.{1}.{2}] should have property: '{3}'".format(property.resource_type,
                                                                                     property.resource_name,
                                                                                     property.property_name,
                                                                                    required_property_name))
        if len(errors) > 0:
            raise AssertionError("\n".join(sorted(errors)))

    def should_not_have_properties(self, properties_list):
        errors = []

        if type(properties_list) is not list:
            properties_list = [properties_list]

        for property in self.properties:
            property_names = property.property_value.keys()
            for excluded_property_name in properties_list:
                if excluded_property_name in property_names:
                    errors.append(
                        "[{0}.{1}.{2}] should not have property: '{3}'".format(property.resource_type,
                                                                               property.resource_name,
                                                                               property.property_name,
                                                                               excluded_property_name))
        if len(errors) > 0:
            raise AssertionError("\n".join(sorted(errors)))

    def find_property(self,regex):
        list = TerraformPropertyList(self.validator)
        for property in self.properties:
            for nested_property in property.property_value:
                if self.validator.matches_regex_pattern(nested_property, regex):
                    list.properties.append(TerraformProperty(property.resource_type,
                                                        "{0}.{1}".format(property.resource_name,property.property_name),
                                                        nested_property,
                                                        property.property_value[nested_property]))
        return list

    def should_match_regex(self,regex):
        errors = []
        for property in self.properties:
            actual_property_value = self.validator.substitute_variable_values_in_string(property.property_value)
            if not self.validator.matches_regex_pattern(actual_property_value, regex):
                errors.append("[{0}.{1}] should match regex '{2}'".format(property.resource_type, "{0}.{1}".format(property.resource_name,property.property_name), regex))

        if len(errors) > 0:
            raise AssertionError("\n".join(sorted(errors)))

    def bool2str(self,bool):
        if str(bool).lower() in ["true"]:
            return "True"
        if str(bool).lower() in ["false"]:
            return "False"
        return bool

    def int2str(self, property_value):
        if type(property_value) is int:
            property_value = str(property_value)
        return property_value

class TerraformProperty:

    def __init__(self,resource_type,resource_name,property_name,property_value):
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.property_name = property_name
        self.property_value = property_value


class TerraformResource:

    def __init__(self,type,name,config):
        self.type = type
        self.name = name
        self.config = config

class TerraformResourceList:

    def __init__(self, validator, resource_types, resources):
        self.resource_list = []

        if type(resource_types) is not list:
            all_resource_types = list(resources.keys())
            regex = resource_types
            resource_types = []
            for resource_type in all_resource_types:
                if validator.matches_regex_pattern(resource_type, regex):
                    resource_types.append(resource_type)

        for resource_type in resource_types:
            if resource_type in resources.keys():
                for resource in resources[resource_type]:
                    self.resource_list.append(TerraformResource(resource_type,resource,resources[resource_type][resource]))

        self.validator = validator

    def property(self, property_name):
        errors = []
        list = TerraformPropertyList(self.validator)
        if len(self.resource_list) > 0:
            for resource in self.resource_list:
                if property_name in resource.config.keys():
                    list.properties.append(TerraformProperty(resource.type,resource.name,property_name,resource.config[property_name]))
                elif self.validator.raise_error_if_property_missing:
                    errors.append("[{0}.{1}] should have property: '{2}'".format(resource.type,resource.name,property_name))

        if len(errors) > 0:
            raise AssertionError("\n".join(sorted(errors)))

        return list

    def find_property(self, regex):
        list = TerraformPropertyList(self.validator)
        if len(self.resource_list) > 0:
            for resource in self.resource_list:
                for property in resource.config:
                    if self.validator.matches_regex_pattern(property, regex):
                        list.properties.append(TerraformProperty(resource.type,
                                                             resource.name,
                                                             property,
                                                             resource.config[property]))
        return list

    def should_have_properties(self, properties_list):
        errors = []

        if type(properties_list) is not list:
            properties_list = [properties_list]

        if len(self.resource_list) > 0:
            for resource in self.resource_list:
                property_names = resource.config.keys()
                for required_property_name in properties_list:
                    if required_property_name not in property_names:
                        errors.append(
                            "[{0}.{1}] should have property: '{2}'".format(resource.type,
                                                                           resource.name,
                                                                           required_property_name))
        if len(errors) > 0:
            raise AssertionError("\n".join(sorted(errors)))

    def should_not_have_properties(self, properties_list):
        errors = []

        if type(properties_list) is not list:
            properties_list = [properties_list]

        if len(self.resource_list) > 0:
            for resource in self.resource_list:
                property_names = resource.config.keys()
                for excluded_property_name in properties_list:
                    if excluded_property_name in property_names:
                        errors.append(
                            "[{0}.{1}] should not have property: '{2}'".format(resource.type,
                                                                               resource.name,
                                                                               excluded_property_name))
        if len(errors) > 0:
            raise AssertionError("\n".join(sorted(errors)))


    def name_should_match_regex(self,regex):
        errors = []
        for resource in self.resource_list:
            if not self.validator.matches_regex_pattern(resource.name, regex):
                errors.append("[{0}.{1}] name should match regex '{2}'".format(resource.type, resource.name, regex))

        if len(errors) > 0:
            raise AssertionError("\n".join(sorted(errors)))

class TerraformVariable:

    def __init__(self,validator,name,value):
        self.validator = validator
        self.name = name
        self.value = value

    def default_value_exists(self):
        errors = []
        if self.value == None:
            errors.append("Variable '{0}' should have a default value".format(self.name))

        if len(errors) > 0:
            raise AssertionError("\n".join(sorted(errors)))

    def default_value_equals(self,expected_value):
        errors = []

        if self.value != expected_value:
            errors.append("Variable '{0}' should have a default value of {1}. Is: {2}".format(self.name,
                                                                                            expected_value,
                                                                                            self.value))
        if len(errors) > 0:
            raise AssertionError("\n".join(sorted(errors)))

    def default_value_matches_regex(self,regex):
        errors = []
        if not self.validator.matches_regex_pattern(self.value, regex):
            errors.append("Variable '{0}' should have a default value that matches regex '{1}'. Is: {2}".format(self.name,regex,self.value))

        if len(errors) > 0:
            raise AssertionError("\n".join(sorted(errors)))

class Validator:

    def __init__(self,path=None):
        self.variable_expand = False
        self.raise_error_if_property_missing = False
        if type(path) is not dict:
            if path is not None:
                self.terraform_config = self.parse_terraform_directory(path)
        else:
            self.terraform_config = path

    def resources(self, type):
        if 'resource' not in self.terraform_config.keys():
            resources = {}
        else:
            resources = self.terraform_config['resource']

        return TerraformResourceList(self, type, resources)

    def variable(self, name):
        return TerraformVariable(self, name, self.get_terraform_variable_value(name))

    def enable_variable_expansion(self):
        self.variable_expand = True

    def disable_variable_expansion(self):
        self.variable_expand = False

    def error_if_property_missing(self):
        self.raise_error_if_property_missing = True

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
        if regex[-1:] != "$":
            regex = regex + "$"

        if regex[0] != "^":
            regex = "^" + regex

        p = re.compile(regex)
        variable = str(variable)
        if '\n' in variable:
            return p.match(variable, re.DOTALL)
        return p.match(variable)

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
        if self.variable_expand:
            if not isinstance(s,dict):
                for variable in self.list_terraform_variables_in_string(s):
                    a = TerraformVariableParser(variable)
                    a.parse()
                    variable_default_value = self.get_terraform_variable_value(a.variable)
                    if variable_default_value != None:
                        for function in a.functions:
                            if function == "lower":
                                variable_default_value = variable_default_value.lower()
                            elif function == "upper":
                                variable_default_value = variable_default_value.upper()
                            else:
                                raise TerraformUnimplementedInterpolationException("The interpolation function '{0}' has not been implemented in Terraform Validator yet. Suggest you run disable_variable_expansion().".format(function))
                        s = s.replace("${" + variable + "}",variable_default_value)
        return s

    def list_terraform_variables_in_string(self, s):
        return re.findall('\${(.*?)}',str(s))

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

    @deprecated
    def assert_variable_base(self, variable_name, closure):
        errors = []
        default_variable_value = self.get_terraform_variable_value(variable_name)
        error = closure(variable_name, default_variable_value)
        if error is not None: errors += error
        if len(errors) > 0:
            raise AssertionError("\n".join(sorted(errors)))

    @deprecated
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
            raise AssertionError("\n".join(sorted(errors)))

    @deprecated
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
            raise AssertionError("\n".join(sorted(errors)))

    def resource_property_value_equals(self, resource_name, resource, resource_type, property, property_value):
        calculated_property_value = self.get_terraform_property_value(property, resource)
        if not (str(calculated_property_value) == str(property_value)):
            return ["[{0}.{1}.{2}] should be '{3}'. Is: '{4}'".format(resource_type, resource_name, property, property_value, calculated_property_value)]
        return []

    @deprecated
    def assert_resource_property_value_equals(self,resource_type,property,property_value):
        def closure(resource_type, resource_name, resource):
            return self.resource_property_value_equals(resource_name, resource, resource_type, property, property_value)
        self.assert_resource_base(resource_type, closure)

    @deprecated
    def assert_nested_resource_property_value_equals(self, resource_type, nested_resource_name, property, property_value):
        def closure(resource_type, resource_name, resource):
            return self.resource_property_value_equals(resource_name, resource, resource_type, property, property_value)
        self.assert_nested_resource_base(resource_type, nested_resource_name, closure)

    def resource_property_value_not_equals(self, resource_name, resource, resource_type, property, property_value):
        calculated_property_value = self.get_terraform_property_value(property, resource)
        if (str(calculated_property_value) == str(property_value)):
            return ["[{0}.{1}.{2}] should not be '{3}'. Is: '{4}'".format(resource_type, resource_name, property, property_value, calculated_property_value)]
        return []

    @deprecated
    def assert_resource_property_value_not_equals(self, resource_type, property, property_value):
        def closure(resource_type, resource_name, resource):
            return self.resource_property_value_not_equals(resource_name, resource, resource_type, property, property_value)
        self.assert_resource_base(resource_type, closure)

    @deprecated
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

    @deprecated
    def assert_resource_has_properties(self,resource_type,required_properties):
        def closure(resource_type, resource_name,resource):
            return self.resource_has_properties(resource_name,resource,resource_type,required_properties)
        self.assert_resource_base(resource_type, closure)

    @deprecated
    def assert_nested_resource_has_properties(self, resource_type, nested_resource_name, required_properties):
        def closure(resource_type, resource_name, resource):
            return self.resource_has_properties(resource_name, resource, resource_type, required_properties)
        self.assert_nested_resource_base(resource_type, nested_resource_name, closure)

    def resource_property_value_matches_regex(self,resource_name,resource,resource_type,property,regex):
        calculated_property_value = self.get_terraform_property_value(property, resource)
        if not self.matches_regex_pattern(str(calculated_property_value), regex):
            return ["[{0}.{1}.{2}] should match regex '{3}'. Is: '{4}'".format(resource_type, resource_name, property, regex, calculated_property_value)]
        return []

    @deprecated
    def assert_resource_property_value_matches_regex(self, resource_type, property, regex):
        def closure(resource_type, resource_name,resource):
            return self.resource_property_value_matches_regex(resource_name, resource, resource_type, property, regex)
        self.assert_resource_base(resource_type, closure)

    @deprecated
    def assert_nested_resource_property_value_matches_regex(self, resource_type, nested_resource_name, property, regex):
        def closure(resource_type, resource_name, resource):
            return self.resource_property_value_matches_regex(resource_name, resource, resource_type, property, regex)
        self.assert_nested_resource_base(resource_type, nested_resource_name, closure)

    @deprecated
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

    @deprecated
    def assert_resource_regexproperty_value_equals(self, resource_type, regex, property_value):
        def closure(resource_type, resource_name,resource):
            return self.resource_regexproperty_value_equals(resource_name,resource,resource_type,regex,property_value)
        self.assert_resource_base(resource_type, closure)

    @deprecated
    def assert_nested_resource_regexproperty_value_equals(self, resource_type, nested_resource_name, regex, property_value):
        def closure(resource_type, resource_name, resource):
            return self.resource_regexproperty_value_equals(resource_name, resource, resource_type, regex, property_value)
        self.assert_nested_resource_base(resource_type, nested_resource_name, closure)

    @deprecated
    def assert_variable_default_value_exists(self, variable_name):
        def closure(variable_name, default_variable_value):
            if default_variable_value == None:
                return ["Variable {0} should have a default value".format(variable_name)]
            return []
        self.assert_variable_base(variable_name, closure)

    @deprecated
    def assert_variable_default_value_equals(self, variable_name, variable_value):
        def closure(variable_name, default_variable_value):
            if str(default_variable_value) != str(variable_value):
                return ["Variable {0} should have a default value of {1}. Is: {2}".format(variable_name, variable_value, default_variable_value)]
            return []
        self.assert_variable_base(variable_name, closure)

    @deprecated
    def assert_variable_default_value_matches_regex(self, variable_name, regex):
        def closure(variable_name, default_variable_value):
            if not self.matches_regex_pattern(default_variable_value, regex):
                return [
                    "Variable {0} should have a default value that matches regex '{1}'. Is: {2}".format(variable_name, regex, default_variable_value)]
            return []
        self.assert_variable_base(variable_name, closure)


