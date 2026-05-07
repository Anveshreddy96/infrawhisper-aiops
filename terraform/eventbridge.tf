resource "aws_cloudwatch_event_rule" "alarm_trigger" {
  name        = "${var.project_name}-alarm-trigger"
  description = "Triggers Lambda when CloudWatch alarm state changes"

  event_pattern = jsonencode({
    source      = ["aws.cloudwatch"]
    detail-type = ["CloudWatch Alarm State Change"]
    detail = {
      state = {
        value = ["ALARM"]
      }
    }
  })
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.alarm_trigger.name
  target_id = "InfraWhisperLambda"
  arn       = aws_lambda_function.triage_engine.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.triage_engine.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.alarm_trigger.arn
}

resource "aws_cloudwatch_metric_alarm" "demo_alarm" {
  alarm_name          = "${var.project_name}-demo-cpu-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Demo alarm for InfraWhisper AIOps project"
  treat_missing_data  = "notBreaching"

  dimensions = {
    InstanceId = "i-placeholder"
  }
}

output "eventbridge_rule_name" {
  value = aws_cloudwatch_event_rule.alarm_trigger.name
}
