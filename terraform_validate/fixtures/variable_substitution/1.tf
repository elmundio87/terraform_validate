variable "test_variable" {
    default = "1"
}

resource "aws_instance" "foo" {
    value = "${var.test_variable}"
}