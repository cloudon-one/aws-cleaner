# AWS - Nightly Clean

This repository contains a Terraform module that will deploy the relevant resources to perform a nightly cleanup of an AWS account (from unused resources)

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.15 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | n/a |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_lambda_function"></a> [lambda\_function](#module\_lambda\_function) | terraform-aws-modules/lambda/aws | 2.7.0 |

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_event_rule.nightly](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_target.nightly_cleanup_lambda_function](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_assume_role_arn"></a> [assume\_role\_arn](#input\_assume\_role\_arn) | ARN of the IAM Role to assume in the member account | `string` | n/a | yes |
| <a name="input_aws_region"></a> [aws\_region](#input\_aws\_region) | AWS Region to deploy all resources | `string` | `"us-east-1"` | no |
| <a name="input_check_all_regions"></a> [check\_all\_regions](#input\_check\_all\_regions) | Whether to check for resources in all regions or just specific ones (default: false = specific) | `bool` | `false` | no |
| <a name="input_default_tags"></a> [default\_tags](#input\_default\_tags) | Tags to apply across all resources handled by this provider | `map(string)` | <pre>{<br>  "Owner": "",<br>  "Terraform": "True",<br>: "True"<br>}</pre> | no |
| <a name="input_dry_run"></a> [dry\_run](#input\_dry\_run) | Whether to run the Lambda in dry-run mode | `bool` | `false` | no |
| <a name="input_event_cron"></a> [event\_cron](#input\_event\_cron) | Cron value for the EventBridge rule | `string` | `"cron(0 20 * * ? *)"` | no |
| <a name="input_function_description"></a> [function\_description](#input\_function\_description) | Description of the Lambda function | `string` | `"Lambda function to cleanup unneeded resources (unattached EBS volumes, unattached EIPs, etc.)"` | no |
| <a name="input_function_name"></a> [function\_name](#input\_function\_name) | Name of the Lambda function | `string` | `"NightlyClean"` | no |
| <a name="input_function_timeout"></a> [function\_timeout](#input\_function\_timeout) | The amount of time your Lambda Function has to run in seconds | `number` | `60` | no |
| <a name="input_keep_tag_key"></a> [keep\_tag\_key](#input\_keep\_tag\_key) | Key of the tag to configure as resoruces to keep | `string` | `"Keep"` | no |

## Outputs

No outputs.
