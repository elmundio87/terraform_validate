import hcl
import os
import re

def get_terraform_resources(name, resources):
    if name not in resources.keys():
        return []
    return resources[name]

def is_terraform_variable(variable):
    p = re.compile('\${var.(.*)}')
    m = p.match(variable)
    if m is None:
        return False
    return True

def get_terraform_variable_name(s):
    p = re.compile('\${var.(.*)}')
    m = p.match(s)
    return m.group(1)

def get_terraform_property_value(name,values,terraform):
    if name not in values:
        return False
    for value in values:
        if(is_terraform_variable(values[value])):
            values[value] = terraform['variable'][get_terraform_variable_name(values[value])]['default']

    return values[name]

def parse_terraform_directory(path="../terraform"):

    terraform_string = ""
    for directory, subdirectories, files in os.walk(path):
         for file in files:
            if(file.endswith(".tf")):
                with open(os.path.join(directory,file)) as fp:
                    terraform_string += fp.read()

    terraform = hcl.loads(terraform_string)
    return terraform

def assert_resource_property_value_equals(terraform,resource_name,property,property_value):
    errors = []
    resources = get_terraform_resources(resource_name,terraform['resource'])
    for resource in resources:
        calculated_property_value = get_terraform_property_value(property,resources[resource],terraform)
        if not str(calculated_property_value) == str(property_value):
            errors += ["[{0}.{1}.{2}] should be '{3}'. Is: '{4}'".format(resource_name,resource, property,property_value,calculated_property_value)]
    if len(errors) > 0:
        raise AssertionError("\n".join(errors))

def assert_nested_resource_property_value_equals(terraform,resource_name,nested_resource_name,property,property_value):
    errors = []
    resources = terraform['resource'][resource_name]
    for resource in resources:
        nested_resources = get_terraform_resources(nested_resource_name,resources[resource])
        if not type(nested_resources) == list:
            nested_resources = [nested_resources]
        for nested_resource in nested_resources:
            calculated_property_value = get_terraform_property_value(property,nested_resource,terraform)
            if not str(calculated_property_value) == str(property_value):
                errors += ["[{0}.{1}.{2}.{3}] should be '{4}'. Is: '{5}'".format(resource_name,resource,nested_resource_name,property,property_value,calculated_property_value)]
    if len(errors) > 0:
        raise AssertionError("\n".join(errors))

def assert_nested_resource_has_properties(terraform,resource_name,nested_resource_name,required_properties):
    errors = []
    resources = terraform['resource'][resource_name]
    for resource in resources:
        property_names = get_terraform_resources(nested_resource_name, resources[resource])
        for required_property_name in required_properties:
            if not required_property_name in property_names:
                errors += ["[{0}.{1}.{2}] should have property: '{3}'".format(resource_name,resource, nested_resource_name,required_property_name)]
    if len(errors) > 0:
        raise AssertionError("\n".join(errors))