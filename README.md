# Terraform Validator

A python package that assists in the enforcement of user-defined standards in Terraform.

The validator uses `pyhcl` to parse Terraform configuration files, then tests the state of the config using custom Asserts.

## Example Usages

### Check that all `aws_ebs_volume` resources are encrypted


```
import unittest
import terraform_validate.terraform_validate as tf
import os

class TestEncryptionAtRest(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"../terraform")
        self.v = tf.Validator(self.path)

    def test_aws_ebs_volume(self):
        self.v.assert_resource_property_value_equals('aws_ebs_volume','encrypted',True)

```

```
resource "aws_ebs_volume" "foo" {
  # This would fail the test
  encrypted = false
}
```

## Assertions

#### assert_resource_property_value_equals(resource,property,value)
For all resources of type `resource`, check that the value of `property` matches `value`

#### assert_nested_resource_property_value_equals(resource,nested_resource,property,value)
For all resources of type `resource`, check that all nested resources of type `nested_resource` have a property called `property` and that its value matches `value`

#### assert_resource_has_properties(resource,nested_resource,properties[])
For all resources of type `resource`, check that they contain all the property names listed in `properties[]`. Any missing properties will cause an `AssertionError`.

#### assert_nested_resource_has_properties(resource,nested_resource,properties[])
For all resources of type `resource`, check that all nested resources of type `nested_resource` contain all the property names listed in `properties[]`. Any missing properties will cause an `AssertionError`.
