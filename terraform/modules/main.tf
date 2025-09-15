terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    template = {
      source = "hashicorp/template"

    }
  }
}

data "aws_region" "current" {}

data "aws_caller_identity" "current" {}

locals {
  usecase_names = [
    "anomaly_detection",
    "data_ingestion",
    "rule_management",
  ]
}

locals {
  usecases_invocation_arns = {
    for usecase in local.usecase_names :
    "${usecase}_lambda_arn" => "arn:aws:apigateway:${data.aws_region.current.name}:lambda:path/2015-03-31/functions/arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${usecase}_function/invocations"
  }
}
