env                         = "dev"
terraform_state_bucket_name = "cirrus-tfstate-store"
code_store_bucket           = "code-utility-store-bucket"
cloudtrail_logs_bucket_name = "cloudtrail-logs-store-bucket"

data_injestion_environment_variables = {
  DYNAMODB_EVENTS_TABLE = "cloud_resource_anomaly_detector_events"
}

rule_management_environment_variables = {
  DYNAMODB_RULES_TABLE = "cloud_resource_anomaly_detector_rules"
}

anomaly_detector_environment_variables = {
  DYNAMODB_EVENTS_TABLE = "cloud_resource_anomaly_detector_events"
  DYNAMODB_RULES_TABLE  = "cloud_resource_anomaly_detector_rules"
  SNS_TOPIC_NAME        = "cloud-anomaly-alerts"
}
