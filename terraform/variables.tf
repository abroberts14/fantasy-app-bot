variable "cloudfront_log_group_name" {
  description = "The name of the CloudFront log group"
  type        = string
  default     = "/ecs/srcbot-chatbot"
}

variable "aws_region" {
  description = "The AWS region"
  type        = string
  default     = "us-east-1"
}