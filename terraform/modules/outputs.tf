output "api_gateway_endpoint" {
  description = "The invoke URL for the API Gateway."
  value       = aws_api_gateway_stage.anomaly_detectpr_api_stage.invoke_url
}

output "sns_topic_arn" {
  description = "The ARN of the SNS topic for alerts. You need to subscribe an endpoint to this topic."
  value       = aws_sns_topic.anomaly_alerts_topic.arn
}

output "usecases_invocation_arns" {
  description = "A map of invocation ARNs for each use case."
  value       = local.usecases_invocation_arns
}
