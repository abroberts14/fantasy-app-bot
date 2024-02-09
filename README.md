# Developing a Single Page App with FastAPI and Vue.js

### Want to learn how to build this?

Check out the [post](https://testdriven.io/blog/developing-a-single-page-app-with-fastapi-and-vuejs).

## Development and Local Testing
Local development:
Build the images and spin up the containers:

```sh
$ docker compose up -d --build
```



Ensure [http://localhost:5000](http://localhost:5000), [http://localhost:5000/docs](http://localhost:5000/docs), and [http://localhost:5173](http://localhost:5173) work as expected.

## Deploying 
When ready to deploy run (do not deply yourself without me) 

```sh
./build_deploy_docker.sh
./deploy.sh
```


Frontend [https://default-alb-1236013653.us-east-1.elb.amazonaws.com/](https://default-alb-1236013653.us-east-1.elb.amazonaws.com/)

Backend [https://default-alb-1236013653.us-east-1.elb.amazonaws.com/api](https://default-alb-1236013653.us-east-1.elb.amazonaws.com/api) work as expected.


Deployments are setup from terraform now:

`terraform/modules/internals` hosts each individual module for the appropriate aws service

- IAM, ECS, VPC etc
-  The `app` and `base` modules leverage these to create the appropriate configurations in aws
-  all services are named using `terraform.workspace` as a prefix, so switching workplaces (https://developer.hashicorp.com/terraform/language/state/workspaces) and deploying will configure all new services with the workspacename-aws-service name
-
![image](https://github.com/abroberts14/fantasy-app-bot/assets/36211649/ac8e4194-59fc-4a17-be90-9ba002084f3b)

`terraform/modules/prod/app` sets up and configures the following aws services:

- ECS cluster
- IAM
- ECS Services for frontend and backend
- Route 53  (broken, and probably shouldnt be here but not sure)

`terraform/modules/prod/base` sets up and configures the following aws services:

- VPC
- Service Discovery (not sure what this is for and if its needed)
- Security Groups
- Application Load Balancer

This outputs all the required information to perform an application deployment:

`alb_dns_name = "default-alb-1236013653.us-east-1.elb.amazonaws.com"
alb_sg_id = "sg-0d96cd9bbf259039a"
app_sg_id = "sg-01bee55a5c474cb08"
base_stack_name = "default"
listener_arn = "arn:aws:elasticloadbalancing:us-east-1:975050074278:listener/app/default-alb/c6e788ff1ad02b24/26796c046a7506f2" 
private_subnet_ids = [
  "subnet-0ce047027cd54c0a1",
  "subnet-0d7821148fcf16367",
"subnet-06d1c54a13289c784",
]
service_discovery_namespace_id = "ns-d5jo7hunjupems4c"
vpc_id = "vpc-0a7d78ad39915d58c"
domain_name = "draftwarroom.com"`


This needs to be placed in `prod/app/variables.tfvars` for the deployment to work.


**Note**:  Setting up another environment by changing terraforms workspace, running the base module will output different variable values associated with this new environment. Deployment to separate environments would use different tfvar files
![image](https://github.com/abroberts14/fantasy-app-bot/assets/36211649/ac8e4194-59fc-4a17-be90-9ba002084f3b)