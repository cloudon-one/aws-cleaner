terraform {
  required_version = ">= 0.15"
}

provider "aws" {
  region = var.aws_region

  assume_role {
    role_arn = var.assume_role_arn
  }

  default_tags {
    tags = var.default_tags
  }
}
