variable "aws_region" {
  type        = string
  description = "AWS Region to deploy all resources"
  default     = "us-east-1"
}

variable "assume_role_arn" {
  description = "ARN of the IAM Role to assume in the member account"
  type        = string
  default     = null
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

variable "dry_run" {
  type        = bool
  description = "Whether to run the Lambda in dry-run mode"
  default     = false
}

variable "check_all_regions" {
  type        = bool
  description = "Whether to check for resources in all regions or just specific ones (default: false = specific)"
  default     = false
}

variable "keep_tag_key" {
  type        = string
  description = "Key of the tag to configure as resoruces to keep"
  default     = "Keep"
}

variable "event_cron" {
  type        = string
  description = "Cron value for the EventBridge rule"
  default     = "cron(0 20 * * ? *)"
}
