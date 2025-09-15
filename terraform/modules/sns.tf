# Define an SNS topic for sending anomaly alerts.
resource "aws_sns_topic" "anomaly_alerts_topic" {
  name = "cloud-anomaly-alerts"
}
