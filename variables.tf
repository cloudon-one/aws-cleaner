variable "aws_region" {
  type        = string
  description = "AWS Region to deploy example API Gateway REST API"
  default     = "us-west-2"
}

variable "default_tags" {
  type        = map(string)
  description = "Tags to apply across all resources handled by this provider"
  default = {
    Terraform = "True"
  }
}

variable "function_name" {
  type        = string
  description = "Name of the Lambda function"
  default     = "NightlyClean"
}
