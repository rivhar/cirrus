resource "aws_dynamodb_table" "resource_events" {
  name         = "cloud_resource_anomaly_detector_events"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "userIdentity"
  range_key    = "eventTime"

  attribute {
    name = "userIdentity"
    type = "S"
  }

  attribute {
    name = "eventTime"
    type = "S"
  }

  attribute {
    name = "eventName"
    type = "S"
  }

  tags = {
    Project = "CloudResourceAnomalyDetector"
  }

  global_secondary_index {
    name            = "EventNameIndex"
    hash_key        = "eventName"
    range_key       = "eventTime"
    projection_type = "ALL"
  }
}

resource "aws_dynamodb_table" "anomaly_rules" {
  name         = "cloud_resource_anomaly_detector_rules"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "ruleId"

  attribute {
    name = "ruleId"
    type = "S"
  }

  tags = {
    Project = "CloudResourceAnomalyDetector"
  }
}
