resource "aws_api_gateway_rest_api" "anomaly_detector_api" {
  name        = var.api_gateway_name
  description = "API for managing anomaly detection rules."
  body        = data.template_file.anomaly_detector_api_swagger.rendered

  lifecycle {
    create_before_destroy = true
  }

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

data "template_file" "anomaly_detector_api_swagger" {
  template = file(var.anomaly_detector_swagger_path)
  vars     = local.usecases_invocation_arns
}

resource "aws_api_gateway_method_settings" "anomaly_detector_apigateway_method_settings" {
  rest_api_id = aws_api_gateway_rest_api.anomaly_detector_api.id
  stage_name  = aws_api_gateway_stage.anomaly_detectpr_api_stage.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled    = true
    logging_level      = "INFO"
    data_trace_enabled = true
    caching_enabled    = true
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [aws_api_gateway_stage.anomaly_detectpr_api_stage]
}


resource "aws_api_gateway_deployment" "anomaly_detector_api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.anomaly_detector_api.id

  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.anomaly_detector_api.body))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [aws_api_gateway_rest_api.anomaly_detector_api]
}

resource "aws_api_gateway_account" "account_settings" {
  cloudwatch_role_arn = aws_iam_role.api_gateway_cloudwatch_role.arn
}

resource "aws_api_gateway_stage" "anomaly_detectpr_api_stage" {
  stage_name    = var.env
  rest_api_id   = aws_api_gateway_rest_api.anomaly_detector_api.id
  deployment_id = aws_api_gateway_deployment.anomaly_detector_api_deployment.id

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_log_group.arn
    format = jsonencode({
      "requestId"      = "$context.requestId",
      "ip"             = "$context.identity.sourceIp",
      "caller"         = "$context.identity.caller",
      "user"           = "$context.identity.user",
      "requestTime"    = "$context.requestTime",
      "httpMethod"     = "$context.httpMethod",
      "resourcePath"   = "$context.resourcePath",
      "status"         = "$context.status",
      "protocol"       = "$context.protocol",
      "responseLength" = "$context.responseLength"
    })
  }

  depends_on = [
    aws_api_gateway_account.account_settings
  ]
}

resource "aws_lambda_permission" "allow_api_gateway_to_invoke_rule_management" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.rule_management.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.anomaly_detector_api.execution_arn}/*/*"
}
