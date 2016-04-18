# Terraform Validator

A python package that assists in the enforcement of user-defined standards in Terraform.

The validator uses `pyhcl` to parse Terraform configuration files, then tests the state of the config using custom Asserts.

# Example Usages

## Check that all `aws_ebs_volume` resources are encrypted


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

## Check that all nested `ebs_block_device` blocks inside `aws_instance` resources are encrypted


```
import unittest
import terraform_validate.terraform_validate as tf
import os

class TestEncryptionAtRest(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"../terraform")
        self.v = tf.Validator(self.path)

    def test_instance_ebs_block_device(self):
        self.v.assert_nested_resource_property_value_equals('aws_instance','ebs_block_device','encrypted',True)

```

```
resource "aws_instance" "foo" {
  ebs_block_device {
    # This would fail the test
    encrypted = false
  }
}
```
