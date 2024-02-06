
resource "aws_cloudwatch_log_group" "ecs_logs" {
  name = var.cloudfront_log_group_name
}
#ENV Vars
variable "DATABASE_URL" { type= string } 
variable "SECRET_KEY" { type= string } 

#Eventually we can set this up to deploy a backend for stage/test env (whatever we want)
#create separate cluster, create separate ecr repository 
#point to a separate db etc
#etc 
module "ecs_module" {
  source             = "./modules/ecs_module"
  app_count          = 1  #horziontal scaling, untested

  #TODO - save these and be able to use different environments 
  ecs_cluster_name   = "src-ecs-cluster-main"
  container_image = "975050074278.dkr.ecr.us-east-1.amazonaws.com/srcbot-ecr-docker-images:backend"  
  container_port = 5000
  container_env_vars = [
    {
      name  = "DATABASE_URL",
      value = var.DATABASE_URL
    },
    {
      name  = "SECRET_KEY",
      value = var.SECRET_KEY
    }
  ]
}

output "load_balancer_ip" {
  value = module.ecs_module.load_balancer_ip
}