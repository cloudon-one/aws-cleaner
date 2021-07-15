variable "aws_region" {
  type        = string
  description = "AWS Region to deploy all resources"
  default     = "us-east-1"
}

variable "default_tags" {
  type        = map(string)
  description = "Tags to apply across all resources handled by this provider"
  default = {
    Terraform       = "True"
    Terraform_Cloud = "True"
    Owner           = "Daniel Vaknin"
  }
}

variable "function_name" {
  type        = string
  description = "Name of the Lambda function"
  default     = "NightlyClean"
}

variable "function_description" {
  type        = string
  description = "Description of the Lambda function"
  default     = "Lambda function to cleanup unneeded resources (unattached EBS volumes, unattached EIPs, etc.)"
}

variable "function_timeout" {
  type        = number
  description = "The amount of time your Lambda Function has to run in seconds"
  default     = 60
}

variable "event_cron" {
  type        = string
  description = "Cron value for the EventBridge rule"
  default     = "cron(0 20 * * ? *)"
}
