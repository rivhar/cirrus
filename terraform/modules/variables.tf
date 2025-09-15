variable "env" {
  description = "Environment name (e.g., dev, staging, prod)."
  type        = string
}

variable "api_gateway_name" {
  description = "The name of the API Gateway."
  type        = string
  default     = "CloudAnomalyDetectorAPI"
}

variable "anomaly_detector_swagger_path" {
  description = "Path to the Swagger file for the API Gateway."
  type        = string
  default     = "../../docs/api/anomaly_detector_api.yml"

}

variable "code_store_bucket" {
  description = "The name of the S3 bucket to store code artifacts."
  type        = string
}

variable "cloudtrail_logs_bucket_name" {
  description = "The name of the S3 bucket to store CloudTrail logs."
  type        = string
}

variable "schedule_expression" {
  description = "The schedule expression for the CloudWatch Event Rule (e.g., rate(15 minutes))"
  type        = string
  default     = "rate(15 minutes)"
}

variable "lambda_runtime" {
  description = "The runtime environment for the Lambda functions."
  type        = string
  default     = "python3.13"
}

variable "lambda_packages_layer_name" {
  description = "The name of the Lambda layer for packages."
  type        = string
  default     = "packages"
}

variable "data_injestion_environment_variables" {
  description = "Environment variables for the data ingestion Lambda function."
  type        = map(string)
}

variable "rule_management_environment_variables" {
  description = "Environment variables for the rule management Lambda function."
  type        = map(string)
}

variable "anomaly_detector_environment_variables" {
  description = "Environment variables for the anomaly detector Lambda function."
  type        = map(string)
}

