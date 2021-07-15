##########################################
# Lambda Function (with various triggers)
##########################################

module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "2.7.0"

  function_name = var.function_name
  description   = "My awesome lambda function"
  handler       = "index.lambda_handler"
  runtime       = "python3.8"
  publish       = true

  source_path = "files/index.py"

  # create_package         = false
  # local_existing_package = "${path.module}/../fixtures/python3.8-zip/existing_package.zip"

  allowed_triggers = {
    NightlyRule = {
      principal  = "events.amazonaws.com"
      source_arn = aws_cloudwatch_event_rule.nightly.arn
    }
  }
}

##################################
# Cloudwatch Events (EventBridge)
##################################
resource "aws_cloudwatch_event_rule" "nightly" {
  name                = "RunNightly"
  description         = "Stops all EC2 instances every night at 10 PM (8 PM GMT)"
  schedule_expression = "cron(0 20 * * ? *)"
}

resource "aws_cloudwatch_event_target" "nightly_cleanup_lambda_function" {
  rule = aws_cloudwatch_event_rule.nightly.name
  arn  = module.lambda_function.lambda_function_arn
}
