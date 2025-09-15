# Define an IAM role that our Lambda function can assume.
resource "aws_iam_role" "data_ingestion_lambda_role" {
  name = "data-ingestion-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

# Attach a policy to the role to allow writing logs to CloudWatch.
resource "aws_iam_role_policy" "lambda_logging_policy" {
  name = "lambda-logging-policy"
  role = aws_iam_role.data_ingestion_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      },
    ]
  })
}

# Attach a policy to the role to allow writing to the DynamoDB table.
resource "aws_iam_role_policy" "lambda_dynamodb_write_policy" {
  name = "lambda-dynamodb-write-policy"
  role = aws_iam_role.data_ingestion_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem"
        ]
        Effect   = "Allow"
        Resource = aws_dynamodb_table.resource_events.arn
      },
    ]
  })
}

# Define an IAM role for the Rule Management Lambda function.
resource "aws_iam_role" "rule_management_lambda_role" {
  name = "rule-management-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

# Attach a policy to allow the Lambda to write logs to CloudWatch.
resource "aws_iam_role_policy" "rule_management_logging_policy" {
  name = "rule-management-logging-policy"
  role = aws_iam_role.rule_management_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      },
    ]
  })
}

# Attach a policy to allow CRUD operations on the anomaly_rules DynamoDB table.
resource "aws_iam_role_policy" "rule_management_dynamodb_policy" {
  name = "rule-management-dynamodb-policy"
  role = aws_iam_role.rule_management_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Scan",
          "dynamodb:DeleteItem"
        ]
        Effect   = "Allow"
        Resource = aws_dynamodb_table.anomaly_rules.arn
      },
    ]
  })
}

# Define an IAM role for the Anomaly Detection Lambda function.
resource "aws_iam_role" "analysis_lambda_role" {
  name = "analysis-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

# Attach a policy to allow logging to CloudWatch.
resource "aws_iam_role_policy" "analysis_logging_policy" {
  name = "analysis-logging-policy"
  role = aws_iam_role.analysis_lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      },
    ]
  })
}

# Attach a policy to allow reading from DynamoDB tables.
resource "aws_iam_role_policy" "analysis_dynamodb_read_policy" {
  name = "analysis-dynamodb-read-policy"
  role = aws_iam_role.analysis_lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = ["dynamodb:Scan", "dynamodb:Query"]
        Effect = "Allow"
        Resource = [
          aws_dynamodb_table.resource_events.arn,
          aws_dynamodb_table.anomaly_rules.arn
        ]
      },
    ]
  })
}

# Attach a policy to allow publishing to the SNS topic.
resource "aws_iam_role_policy" "analysis_sns_publish_policy" {
  name = "analysis-sns-publish-policy"
  role = aws_iam_role.analysis_lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "sns:Publish"
        Effect   = "Allow"
        Resource = aws_sns_topic.anomaly_alerts_topic.arn
      },
    ]
  })
}


# Define an IAM role for GitHub Actions to assume for deployments.
resource "aws_iam_role" "github_actions_deploy_role" {
  name = "github_actions_deploy_role"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Federated" : "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/token.actions.githubusercontent.com"
        },
        "Action" : "sts:AssumeRoleWithWebIdentity",
        "Condition" : {
          "StringLike" : {
            "token.actions.githubusercontent.com:sub" : "repo:rivhar/cirrus:*"
          },
          "StringEquals" : {
            "token.actions.githubusercontent.com:aud" : "sts.amazonaws.com"
          }
        }
      }
    ]
  })
}

resource "aws_iam_policy" "github_actions_deploy_policy" {
  name        = "github-actions-deploy-policy"
  description = "Policy for GitHub Actions deployment role"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "DynamoDBPermissions",
        "Effect" : "Allow",
        "Action" : [
          "dynamodb:CreateTable",
          "dynamodb:DeleteTable",
          "dynamodb:DescribeTable",
          "dynamodb:UpdateTable"
        ],
        "Resource" : "arn:aws:dynamodb:*:*:table/*"
      },
      {
        "Sid" : "LambdaPermissions",
        "Effect" : "Allow",
        "Action" : [
          "lambda:CreateFunction",
          "lambda:DeleteFunction",
          "lambda:GetFunction",
          "lambda:UpdateFunctionConfiguration",
          "lambda:AddPermission",
          "lambda:RemovePermission",
          "lambda:UpdateFunctionCode"
        ],
        "Resource" : "arn:aws:lambda:*:*:function:*"
      },
      {
        "Sid" : "IAMPermissions",
        "Effect" : "Allow",
        "Action" : [
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:GetRole",
          "iam:TagRole",
          "iam:AttachRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:DetachRolePolicy",
          "iam:PutRolePolicy",
          "iam:PassRole"
        ],
        "Resource" : "arn:aws:iam::*:role/*"
      },
      {
        "Sid" : "APIGatewayPermissions",
        "Effect" : "Allow",
        "Action" : [
          "apigateway:GET",
          "apigateway:POST",
          "apigateway:PUT",
          "apigateway:DELETE",
          "apigateway:PATCH"
        ],
        "Resource" : "arn:aws:apigateway:*::/*"
      },
      {
        "Sid" : "CloudWatchEventsPermissions",
        "Effect" : "Allow",
        "Action" : [
          "events:PutRule",
          "events:RemoveTargets",
          "events:PutTargets",
          "events:DeleteRule",
          "events:DescribeRule",
          "events:PutPermission",
          "events:RemovePermission"
        ],
        "Resource" : "arn:aws:events:*:*:rule/*"
      },
      {
        "Sid" : "SNSPermissions",
        "Effect" : "Allow",
        "Action" : [
          "sns:CreateTopic",
          "sns:DeleteTopic",
          "sns:Publish",
          "sns:SetTopicAttributes"
        ],
        "Resource" : "arn:aws:sns:*:*:*"
      },
      {
        "Sid" : "CloudWatchLogsPermissions",
        "Effect" : "Allow",
        "Action" : [
          "logs:CreateLogGroup",
          "logs:DescribeLogGroups"
        ],
        "Resource" : "arn:aws:logs:*:*:log-group:*"
      },
      {
        "Sid" : "S3Permissions",
        "Effect" : "Allow",
        "Action" : [
          "s3:CreateBucket",
          "s3:DeleteBucket",
          "s3:ListBucket",
          "s3:PutBucketPublicAccessBlock",
          "s3:PutBucketVersioning",
          "s3:PutBucketLifecycleConfiguration",
          "s3:PutBucketEncryption",
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject"
        ],
        "Resource" : "arn:aws:s3:::*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "github_actions_deploy_policy_attachment" {
  role       = aws_iam_role.github_actions_deploy_role.name
  policy_arn = aws_iam_policy.github_actions_deploy_policy.arn
}

# Grant the CloudWatch Event Rule permission to invoke our Lambda function.
resource "aws_lambda_permission" "allow_cloudwatch_to_invoke_data_ingestion" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.data_ingestion.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.cloudtrail_rule.arn
}

# Grant the CloudWatch Event Rule permission to invoke the Anomaly Detector Lambda.
resource "aws_lambda_permission" "allow_cloudwatch_to_invoke_detector" {
  statement_id  = "AllowExecutionFromCloudWatchSchedule"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.anomaly_detector.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.anomaly_detector_schedule.arn
}

resource "aws_s3_bucket_policy" "cloudtrail_policy" {
  bucket = aws_s3_bucket.cloudtrail_logs.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.cloudtrail_logs.arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      },
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail_logs.arn
      }
    ]
  })
}

# 2. Create an IAM role for API Gateway to assume.
resource "aws_iam_role" "api_gateway_cloudwatch_role" {
  name = "APIGatewayCloudWatchLogsRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
      },
    ]
  })
}

# 3. Attach the managed policy for CloudWatch Logs to the IAM role.
resource "aws_iam_role_policy_attachment" "api_gateway_cloudwatch_logs" {
  role       = aws_iam_role.api_gateway_cloudwatch_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}
