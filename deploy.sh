#!/bin/bash

TERRAFORM_DIR="terraform/modules/prod/app"

cd $TERRAFORM_DIR

ls 
terraform init
echo "Current directory: $(pwd)"
echo "Environment Variables: $(printenv)"
echo "creating tf plan..."
terraform plan -out=tfplan -var-file="variables.tfvars"

echo "applying tf plan..."
terraform apply "tfplan"

echo "deployment finished."
