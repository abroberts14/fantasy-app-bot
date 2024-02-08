###############################################################################
# ECS
###############################################################################

module "ecs" {
  source = "../../internal/ecs/ad-hoc/cluster"
}

###############################################################################
# IAM
###############################################################################

module "iam" {
  source = "../../internal/iam"
}

###############################################################################
# Common variables for ECS Services and Tasks
###############################################################################

data "aws_caller_identity" "current" {}

locals {
  env_vars = [
    {
      name  = "DATABASE_URL"
      value = "postgres://postgres:postgres1!@srcbot1.c7okouiqu9jh.us-east-1.rds.amazonaws.com:5432/srcbot1"
    },
    {
      name  = "SECRET_KEY"
      value = "09d25e094faa6caaaron8166b7a9563b93f79f6f0f4caa6cf63b88e8d3e7"
    }
    
  ]
  be_image  = "${data.aws_caller_identity.current.account_id}.dkr.ecr.us-east-1.amazonaws.com/srcbot-ecr-docker-images:backend"
  fe_image  = "${data.aws_caller_identity.current.account_id}.dkr.ecr.us-east-1.amazonaws.com/srcbot-ecr-docker-images:frontend"
  # 975050074278.dkr.ecr.us-east-1.amazonaws.com/srcbot-ecr-docker-images:backend
  # 975050074278.dkr.ecr.us-east-1.amazonaws.com/backend:latest
  host_name = "${terraform.workspace}.${var.domain_name}"
}
###############################################################################
# Gunicorn ECS Service
###############################################################################

module "api" {
  source             = "../../internal/ecs/ad-hoc/web"
  name               = "gunicorn"
  ecs_cluster_id     = module.ecs.cluster_id
  task_role_arn      = module.iam.task_role_arn
  execution_role_arn = module.iam.execution_role_arn
  app_sg_id          = var.app_sg_id
  command            = var.api_command
  env_vars           = concat(local.env_vars, var.extra_env_vars)
  image              = local.be_image
  cpu                = var.api_cpu
  memory             = var.api_memory
  port               = 5000
  path_patterns      = ["/api/*"]
  health_check_path  = "/api/health-check/"
  listener_arn       = var.listener_arn
  vpc_id             = var.vpc_id
  private_subnet_ids = var.private_subnet_ids
  host_name          = local.host_name
  region             = var.region
}

###############################################################################
# Frontend ECS Service
###############################################################################

module "web-ui" {
  source             = "../../internal/ecs/ad-hoc/web"
  name               = "web-ui"
  ecs_cluster_id     = module.ecs.cluster_id
  app_sg_id          = var.app_sg_id
  task_role_arn      = module.iam.task_role_arn
  execution_role_arn = module.iam.execution_role_arn
  command            = var.frontend_command
  env_vars           = [
    {
      name  = "VITE_APP_BACKEND_URL",
      value = "https://default-alb-1236013653.us-east-1.elb.amazonaws.com/api"
    }
  ]

  image              = local.fe_image
  region             = var.region
  cpu                = var.frontend_cpu
  memory             = var.frontend_memory
  port               = 5173
  path_patterns      = ["/*"]
  health_check_path  = "/"
  listener_arn       = var.listener_arn
  vpc_id             = var.vpc_id
  private_subnet_ids = var.private_subnet_ids
  host_name          = local.host_name

  # this is needed in order to for the listener rule priorities to work correctly
  # without explicitly being set
  depends_on = [module.api]
}

###############################################################################
# Route 53
###############################################################################

module "route53" {
  source       = "../../internal/route53"
  alb_dns_name = var.alb_dns_name
  domain_name  = var.domain_name
}
