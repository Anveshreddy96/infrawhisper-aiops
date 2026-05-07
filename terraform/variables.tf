variable "project_name" {
  description = "Name prefix for all resources"
  type        = string
  default     = "infrawhisper"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "bedrock_model_id" {
  description = "Claude model ID in Bedrock"
  type        = string
  default     = "us.anthropic.claude-sonnet-4-6"
}
