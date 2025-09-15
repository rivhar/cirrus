data "aws_s3_object" "data_ingestion_package" {
  bucket = aws_s3_bucket.code_store.id
  key    = "data_injestion_lambda_package/data_injestion.zip"
}

data "aws_s3_object" "data_ingestion_package_sha256" {
  bucket = aws_s3_bucket.code_store.id
  key    = "data_injestion_lambda_package/data_injestion.zip.sha256"
}

# Define the Lambda function itself.
resource "aws_lambda_function" "data_ingestion" {
  function_name    = "data_ingestion_function"
  s3_bucket        = data.aws_s3_object.data_ingestion_package.bucket
  s3_key           = data.aws_s3_object.data_ingestion_package.key
  source_code_hash = chomp(data.aws_s3_object.data_ingestion_package_sha256.body)
  description      = "Lambda function for ingesting CloudTrail events into DynamoDB."

  role        = aws_iam_role.data_ingestion_lambda_role.arn
  handler     = "src.lambda_function.lambda_handler"
  runtime     = var.lambda_runtime
  memory_size = 128
  timeout     = 30

  tags = {
    Name        = "data-ingestion-function"
    Environment = var.env
  }

  layers = [
    aws_lambda_layer_version.packages_layer.arn
  ]
  # We'll use this environment variable in our Python code to get the table name.
  environment {
    variables = var.data_injestion_environment_variables
  }
}

data "aws_s3_object" "rule_management_package" {
  bucket = aws_s3_bucket.code_store.id
  key    = "rule_management_lambda_package/rule_management.zip"
}

data "aws_s3_object" "rule_management_package_sha256" {
  bucket = aws_s3_bucket.code_store.id
  key    = "rule_management_lambda_package/rule_management.zip.sha256"
}

# Define the Lambda function that will manage the rules.
resource "aws_lambda_function" "rule_management" {
  function_name    = "rule_management_function"
  s3_bucket        = data.aws_s3_object.rule_management_package.bucket
  s3_key           = data.aws_s3_object.rule_management_package.key
  source_code_hash = chomp(data.aws_s3_object.rule_management_package_sha256.body)
  description      = "Lambda function for managing anomaly rules."

  role        = aws_iam_role.rule_management_lambda_role.arn
  handler     = "src.lambda_function.lambda_handler"
  runtime     = var.lambda_runtime
  memory_size = 128
  timeout     = 30

  tags = {
    Name        = "rule-management-function"
    Environment = var.env
  }

  layers = [
    aws_lambda_layer_version.packages_layer.arn
  ]

  environment {
    variables = var.rule_management_environment_variables
  }
}


data "aws_s3_object" "anomaly_detector_package" {
  bucket = aws_s3_bucket.code_store.id
  key    = "anomaly_detector_lambda_package/anomaly_detector.zip"
}


data "aws_s3_object" "anomaly_detector_package_sha256" {
  bucket = aws_s3_bucket.code_store.id
  key    = "anomaly_detector_lambda_package/anomaly_detector.zip.sha256"
}

# Define the Anomaly Detection Lambda function.
resource "aws_lambda_function" "anomaly_detector" {
  function_name    = "anomaly_detector_function"
  s3_bucket        = data.aws_s3_object.anomaly_detector_package.bucket
  s3_key           = data.aws_s3_object.anomaly_detector_package.key
  source_code_hash = chomp(data.aws_s3_object.anomaly_detector_package_sha256.body)
  description      = "Lambda function for anomaly detection."

  role        = aws_iam_role.analysis_lambda_role.arn
  handler     = "src.lambda_function.lambda_handler"
  runtime     = var.lambda_runtime
  memory_size = 128
  timeout     = 300

  tags = {
    Name        = "anomaly-detector-function"
    Environment = var.env
  }

  layers = [
    aws_lambda_layer_version.packages_layer.arn
  ]

  environment {
    variables = var.anomaly_detector_environment_variables
  }
}
