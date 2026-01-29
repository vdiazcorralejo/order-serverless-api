environment = "dev"
aws_region  = "eu-west-1"

# API Gateway settings
api_throttle_burst_limit = 100
api_throttle_rate_limit  = 50

# DynamoDB settings
dynamodb_billing_mode = "PAY_PER_REQUEST"

# Tags
tags = {
  CostCenter = "Development"
  Owner      = "DevOps Team"
}
