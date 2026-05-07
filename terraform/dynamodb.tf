resource "aws_dynamodb_table" "incidents" {
  name           = "${var.project_name}-incidents"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "incident_id"

  attribute {
    name = "incident_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  global_secondary_index {
    name            = "timestamp-index"
    hash_key        = "timestamp"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "expiry_time"
    enabled        = true
  }

  tags = {
    Project = var.project_name
    Purpose = "Store AI-analyzed incidents"
  }
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.incidents.name
}
