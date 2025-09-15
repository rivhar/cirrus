# --- CloudWatch Logging Resources ---
# 1. Create a CloudWatch Log Group for the API Gateway logs.
resource "aws_cloudwatch_log_group" "api_gateway_log_group" {
  name = "/aws/apigateway/${aws_api_gateway_rest_api.anomaly_detector_api.name}"

  tags = {
    Name = "API Gateway Logs for Anomaly Detector"
  }
}
