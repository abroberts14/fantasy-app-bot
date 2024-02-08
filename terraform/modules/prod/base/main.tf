###############################################################################
# VPC
###############################################################################

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "${terraform.workspace}-vpc"
  cidr = var.cidr

  azs             = var.azs
  private_subnets = var.private_subnet_ids
  public_subnets  = var.public_subnets

  enable_nat_gateway     = true
  single_nat_gateway     = true
  one_nat_gateway_per_az = false

  # DNS settings
  enable_dns_hostnames = true
  enable_dns_support   = true
}

###############################################################################
# Service Discovery (Cloud Map)
###############################################################################

module "sd" {
  source = "../../internal/sd"
  vpc_id = module.vpc.vpc_id
}


###############################################################################
# Security groups
###############################################################################

module "sg" {
  source = "../../internal/sg"
  vpc_id = module.vpc.vpc_id
}

###############################################################################
# Load Balancer
###############################################################################

module "lb" {
  source          = "../../internal/alb"
  vpc_id          = module.vpc.vpc_id
  public_subnets  = module.vpc.public_subnets
  alb_sg_id       = module.sg.alb_sg_id
  certificate_arn = var.certificate_arn
}
