variable "app_count" {
  description = "Number of application instances"
  type        = number
}

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

variable "ecs_cluster_name" {
  description = "The name of the ECS cluster"
  type        = string
  default     = "src-main-cluster"
}

variable "ecs_security_group_name" {
  description = "The name of the ECS security group"
  type        = string
  default     = "src-task-security-group"
}

variable "ecs_service_name" {
  description = "The name of the ECS service"
  type        = string
  default     = "src-ecs-service"
}

variable "ecs_task_family" {
  description = "The family of the ECS task definition"
  type        = string
  default     = "src-app-backend"
}

variable "ecs_task_cpu" {
  description = "The number of CPU units used by the task"
  type        = number
  default     = 1024
}

variable "ecs_task_memory" {
  description = "The amount of memory used by the task (in MiB)"
  type        = number
  default     = 2048
}

variable "container_image" {
  description = "The image used to start a container"
  type        = string
}

variable "container_port" {
  description = "The port on which the container will listen"
  type        = number
  default     = 5000
}

variable "container_env_vars" {
  description = "Environment variables for the container"
  type        = list(map(string))
  default     = []
}

variable "lb_name" {
  description = "The name of the loadbalaner"
  type        = string
  default     = "src-lb"
}

variable "lb_target_group_name" {
  description = "The name of the loadbalaner target group"
  type        = string
  default     = "src-target-group"
}

