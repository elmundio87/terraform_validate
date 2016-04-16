resource "aws_instance" "foo" {

    nested_resource {
        value = 1
        value2 = 2
    }

}