##########################################
# Lambda Function (with various triggers)
##########################################

module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "4.0.2"

  function_name = var.function_name
  description   = var.function_description
  handler       = "index.lambda_handler"
  runtime       = "python3.9"
  publish       = true
  timeout       = var.function_timeout

  source_path = "files/index.py"

  attach_policy = true
  policy        = "arn:aws:iam::aws:policy/AdministratorAccess"

  environment_variables = {
    CHECK_ALL_REGIONS = var.check_all_regions
    KEEP_TAG_KEY      = var.keep_tag_key["auto-deletion"]
    DRY_RUN           = var.dry_run
    EMAIL_IDENTITY    = var.email_identity
    TO_ADDRESS        = var.to_address
  }

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
  schedule_expression = var.event_cron
}

resource "aws_cloudwatch_event_target" "nightly_cleanup_lambda_function" {
  rule = aws_cloudwatch_event_rule.nightly.name
  arn  = module.lambda_function.lambda_function_arn
}
