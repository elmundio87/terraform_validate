# Terraform Validator

[![Build Status](https://travis-ci.org/elmundio87/terraform_validator.svg?branch=master)](https://travis-ci.org/elmundio87/terraform_validator)

A python package that assists in the enforcement of user-defined standards in Terraform.

The validator uses `pyhcl` to parse Terraform configuration files, then tests the state of the config using custom Asserts.

## Example Usages

### Check that all AWS EBS volumes are encrypted


```
class TestEncryptionAtRest(unittest.TestCase):

    def setUp(self):
        self.path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"../terraform")
        self.v = terraform_validate.Validator(self.path)

    def test_aws_ebs_volume(self):
        self.v.assert_resource_property_value_equals('aws_ebs_volume','encrypted',True)

    def test_instance_ebs_block_device(self):
        self.v.assert_nested_resource_property_value_equals('aws_instance','ebs_block_device','encrypted',True)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEncryptionAtRest)
    unittest.TextTestRunner(verbosity=0).run(suite)

```

```
resource "aws_instance" "foo" {
  # This would fail the test
  ebs_block_device{
    encrypted = false
  }
}

resource "aws_ebs_volume" "bar" {
  # This would fail the test
  encrypted = false
}
```

## Assertions

All Asserts accept `resource_type` as a list or a string

eg.

```
# Pass in a string
assert_resource_property_value_equals('aws_ebs_volume','encrypted',True)

# Pass in a list
resource_types = ['aws_ebs_volume','aws_another_type_of_volume']
assert_resource_property_value_equals(resource_types,'encrypted',True)
```

#### assert_resource_property_value_equals(resource_type, property, value)
For all resources of type `resource_type`, check that the value of `property` equals `value`

#### assert_nested_resource_property_value_equals(resource_type,nested_resource_type,property,value)
For all resources of type `resource_type`, check that all nested resources of type `nested_resource_type` have a property called `property` and that its value equals `value`

#### assert_resource_has_properties(resource_type,nested_resource_type,properties[])
For all resources of type `resource_type`, check that they contain all the property names listed in `properties[]`. Any missing properties will cause an `AssertionError`.

#### assert_nested_resource_has_properties(resource_type,nested_resource_type,properties[])
For all resources of type `resource_type`, check that all nested resources of type `nested_resource_type` contain all the property names listed in `properties[]`. Any missing properties will cause an `AssertionError`.

#### assert_resource_property_value_matches_regex(resource_type, property, regex)
For all resources of type `resource_type`, check that the value of `property` matches regex `regex`

#### assert_nested_resource_property_value_matches_regex(resource_type, nested_resource_type, property, regex)
For all resources of type `resource_type`, ccheck that all nested resources of type `nested_resource_type` have a property called `property` and that its value matches regex `regex`

#### assert_resource_regexproperty_value_equals(resource_type, regex, value
For all resources of type `resource_type`, check that all nested resources of type `nested_resource_type` has a property that matches `regex`, and that its value is set to `value`
