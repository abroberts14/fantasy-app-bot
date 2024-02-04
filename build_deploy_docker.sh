#!/bin/bash
region="us-east-1"
account_id="296515499043" #update with new aws account id
repository_name="srcbot"

declare -A services=( ["backend"]="./services/backend" ["frontend"]="./services/frontend" ["chatbot"]="./services/baseball_bot" )

echo "authenticate docker with ecr..."
aws ecr get-login-password --region $region | docker login --username AWS --password-stdin $account_id.dkr.ecr.$region.amazonaws.com

for service in "${!services[@]}"; do
  echo "building $service..."
  docker build -t $service ${services[$service]}

  echo "tagging image -  $service..."
  docker tag $service:latest $account_id.dkr.ecr.$region.amazonaws.com/$repository_name:$service

  echo "pushing $service to ecr..."
  docker push $account_id.dkr.ecr.$region.amazonaws.com/$repository_name:$service
done

echo "doneso"