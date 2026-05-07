output "project_summary" {
  value = {
    dynamodb_table   = aws_dynamodb_table.incidents.name
    lambda_function  = aws_lambda_function.triage_engine.function_name
    eventbridge_rule = aws_cloudwatch_event_rule.alarm_trigger.name
    bedrock_model    = var.bedrock_model_id
    region           = var.aws_region
  }
  description = "InfraWhisper infrastructure summary"
}
