# Package Lambda function
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src/orders"
  output_path = "${path.module}/lambda_function.zip"
}

# Lambda Function
resource "aws_lambda_function" "orders_api" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${local.resource_prefix}-orders-api"
  role            = aws_iam_role.lambda_execution.arn
  handler         = "handler.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.orders.name
      ENVIRONMENT    = var.environment
      LOG_LEVEL      = var.environment == "prod" ? "INFO" : "DEBUG"
    }
  }

  # Enable X-Ray tracing in production
  tracing_config {
    mode = var.environment == "prod" ? "Active" : "PassThrough"
  }

  tags = {
    Name = "${local.resource_prefix}-orders-api"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.orders_api.function_name}"
  retention_in_days = var.environment == "prod" ? 30 : 7

  tags = {
    Name = "${local.resource_prefix}-lambda-logs"
  }
}

# Lambda Permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.orders_api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}
