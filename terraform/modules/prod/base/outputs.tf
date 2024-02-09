output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnet_ids" {
  value = module.vpc.private_subnets
}

output "app_sg_id" {
  value = module.sg.app_sg_id
}

output "alb_sg_id" {
  value = module.sg.alb_sg_id
}

output "listener_arn" {
  value = module.lb.listener_arn
}

output "alb_dns_name" {
  value = module.lb.alb_dns_name
}

output "service_discovery_namespace_id" {
  value       = module.sd.service_discovery_namespace_id
  description = "service discovery namespace id"
}

output "base_stack_name" {
  value = terraform.workspace
}