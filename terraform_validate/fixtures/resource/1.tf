resource "aws_instance" "foo" {

    value = 1
    value2 = 2

}

resource "aws_instance" "bar" {

    value = 1
    value2 = 2

    propertylist {
        value = 2
    }

}

resource "aws_elb" "buzz" {

    value = 1

}