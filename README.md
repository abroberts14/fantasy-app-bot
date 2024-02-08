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