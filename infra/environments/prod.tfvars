environment = "prod"
aws_region  = "eu-west-1"

# API Gateway settings
api_throttle_burst_limit = 500
api_throttle_rate_limit  = 250

# DynamoDB settings
dynamodb_billing_mode = "PAY_PER_REQUEST"

# Tags
tags = {
  CostCenter = "Production"
  Owner      = "Platform Team"
}
