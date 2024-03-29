variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "app_sg_id" {
  type        = string
  description = "App Security Group ID"
}

variable "alb_sg_id" {
  type        = string
  description = "ALB Security Group ID"
}

# Load balancer

variable "listener_arn" {
  type = string
}

variable "alb_dns_name" {
  type        = string
  description = "DNS name of the shared ALB"
}

# Service Discovery

variable "service_discovery_namespace_id" {
  type = string
}



##############################################################################
# AWS
##############################################################################

variable "region" {
  default = "us-east-1"
}


# Application

##############################################################################
# Route 53
##############################################################################

variable "domain_name" {
  description = "Domain name to be used for Route 53 records (e.g. example.com)"
  type        = string
}

##############################################################################
# Application Services - Gunicorn, Celery, Beat, frontend SPA, etc.
##############################################################################

# Shared

variable "extra_env_vars" {
  description = "User-defined environment variables to pass to the backend service and task containers (api, worker, migrate, etc.)"
  type        = list(object({ name = string, value = string }))
  default     = []
  
}

variable "frontend_command" {
  description = "Command to run in the frontend container"
  default     = ["npm", "run", "dev"]
  type        = list(string)
}

variable "frontend_cpu" {
  default     = 1024
  description = "CPU to allocate to container for the frontend task"
  type        = number
}

variable "frontend_memory" {
  default     = 2048
  description = "Amount (in MiB) of memory used by the frontend task"
  type        = number
}

# api

variable "api_command" {
  description = "Command used to start backend API container"
  #default     = ["uvicorn", "src.main:app", "--host", "0.0.0.0",  "--port", "5000"]
  default = ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-t", "1000", "-b", "0.0.0.0:5000", "--log-level", "info", "src.main:app"]
  type        = list(string)
}
variable "api_cpu" {
  default     = 1024
  description = "CPU to allocate to container"
  type        = number
}

variable "api_memory" {
  default     = 2048
  description = "Amount (in MiB) of memory used by the task"
  type        = number
}

# backend_update commands (migrate, collectstatic)

variable "backend_update_command" {
  description = "Command used to run database migrations and collectstatic"
  default     = ["python", "manage.py", "pre_update"]
  type        = list(string)
}

variable "backend_update_cpu" {
  default     = 1024
  description = "CPU to allocate to container"
  type        = number
}

variable "backend_update_memory" {
  default     = 2048
  description = "Amount (in MiB) of memory used by the task"
  type        = number
}


variable "base_stack_name" {
  description = "Name of the base stack that the ad hoc env is created in."
  type        = string
}
