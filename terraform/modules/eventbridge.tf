resource "aws_cloudwatch_event_rule" "anomaly_detector_schedule" {
  name                = "anomaly-detector-schedule"
  description         = "Triggers the anomaly detector function based on a defined schedule."
  schedule_expression = var.schedule_expression # e.g., "rate(15 minutes)"
}

resource "aws_cloudwatch_event_target" "detector_target" {
  rule = aws_cloudwatch_event_rule.anomaly_detector_schedule.name
  arn  = aws_lambda_function.anomaly_detector.arn
}

resource "aws_cloudwatch_event_rule" "cloudtrail_rule" {
  name        = "cloud-anomaly-rule"
  description = "Trigger for critical AWS management events"
  event_pattern = jsonencode({
    source        = ["aws.iam", "aws.ec2", "aws.s3", "aws.dynamodb"],
    "detail-type" = ["AWS API Call via CloudTrail"],
    detail = {
      eventSource = [
        "ec2.amazonaws.com",
        "s3.amazonaws.com",
        "iam.amazonaws.com",
        "dynamodb.amazonaws.com"
      ],
      eventName = [
        "RunInstances",
        "TerminateInstances",
        "CreateBucket",
        "DeleteBucket",
        "PutBucketPolicy",
        "AttachRolePolicy",
        "CreateRole",
        "DeleteRole",
        "CreateTable",
        "DeleteTable",
        "UpdateTable"
      ],
      eventCategory   = ["Management"],
      managementEvent = [true]
    }
  })
}

resource "aws_cloudwatch_event_target" "data_ingestion_target" {
  rule = aws_cloudwatch_event_rule.cloudtrail_rule.name
  arn  = aws_lambda_function.data_ingestion.arn
}
