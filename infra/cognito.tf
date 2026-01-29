resource "aws_cognito_user_pool" "main" {
  name = "${local.resource_prefix}-user-pool"

  # Password policy
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_uppercase = true
    require_numbers   = true
    require_symbols   = true
  }

  # Auto-verified attributes
  auto_verified_attributes = ["email"]

  # User attributes
  schema {
    name                = "email"
    attribute_data_type = "String"
    required            = true
    mutable             = true

    string_attribute_constraints {
      min_length = 1
      max_length = 256
    }
  }

  # Account recovery
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  tags = {
    Name = "${local.resource_prefix}-user-pool"
  }
}

# User Pool Client
resource "aws_cognito_user_pool_client" "main" {
  name         = "${local.resource_prefix}-client"
  user_pool_id = aws_cognito_user_pool.main.id

  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_ADMIN_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]

  # Token validity
  access_token_validity  = 1  # hours
  id_token_validity      = 1  # hours
  refresh_token_validity = 30 # days

  token_validity_units {
    access_token  = "hours"
    id_token      = "hours"
    refresh_token = "days"
  }

  prevent_user_existence_errors = "ENABLED"
}

# User Pool Domain (for hosted UI - optional)
resource "aws_cognito_user_pool_domain" "main" {
  domain       = "${local.resource_prefix}-${random_string.cognito_domain_suffix.result}"
  user_pool_id = aws_cognito_user_pool.main.id
}

# Random suffix for Cognito domain (must be globally unique)
resource "random_string" "cognito_domain_suffix" {
  length  = 8
  special = false
  upper   = false
}
