resource "aws_dynamodb_table" "orders" {
  name           = "${local.resource_prefix}-orders"
  billing_mode   = var.dynamodb_billing_mode
  hash_key       = "order_id"
  
  attribute {
    name = "order_id"
    type = "S"
  }

  attribute {
    name = "customer_id"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "S"
  }

  # GSI for querying by customer
  global_secondary_index {
    name            = "CustomerIndex"
    hash_key        = "customer_id"
    range_key       = "created_at"
    projection_type = "ALL"
  }

  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = var.environment == "prod" ? true : false
  }

  # Server-side encryption
  server_side_encryption {
    enabled = true
  }

  # TTL (optional, for automatic cleanup)
  ttl {
    attribute_name = "ttl"
    enabled        = false
  }

  tags = {
    Name = "${local.resource_prefix}-orders"
  }
}
