##############################################################################
# VPC
##############################################################################

variable "cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "azs" {
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
  description = "AZs to use for VPC"
  type        = list(string)
}

variable "private_subnet_ids" {
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  description = "Private subnets to use for VPC"
  type        = list(string)
}

variable "public_subnets" {
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  description = "Public subnets to use for VPC"
  type        = list(string)
}

variable "certificate_arn" {
  default = "arn:aws:acm:us-east-1:975050074278:certificate/89e991b7-46f5-4ebe-b843-7943ff4ca6e5"
  description = "ARN of the certificate to use for the ALB"
  type        = string
}

