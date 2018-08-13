resource "aws_iam_role" "cst_security_agent_lambda_execution_role" {
  name = "${var.prefix}_CstSecurityAgentLambdaExecutionRole"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}


resource "aws_iam_role_policy" "cst_security_agent_role_policy" {
  name = "${var.prefix}_CstSecurityAgentRolePolicy"
  role = "${aws_iam_role.cst_security_agent_lambda_execution_role.id}"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Statement0",
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "arn:aws:iam::*:role/*CstSecurityInspectorRole"
        }
    ]
}
EOF
}