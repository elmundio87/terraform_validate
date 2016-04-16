resource "aws_instance" "foo" {

    nested_resource {
        value = 1
    }

}