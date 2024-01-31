FROM python:3.11-buster

RUN mkdir app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

ENV AWS_DEFAULT_REGION=us-east-1
ENV AWS_ACCESS_KEY_ID=SetFromEnvVarMustBeAarons
ENV AWS_SECRET_ACCESS_KEY=SetFromEnvVarMustBeAarons
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#install aws cli and other packages required to install aws 
RUN apt-get update && \
    apt-get install -y \
        unzip \
        curl \
    && apt-get clean \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf \
        awscliv2.zip \
    && apt-get -y purge curl \
    && apt-get -y purge unzip 
#TODO: env vars to get the user id of whoever is starting the bot/running the docker container
RUN export user_id=1
COPY . .
COPY . .
RUN aws s3 cp s3://usersessiontokens/auth${user_id}/ bot/auth --recursive
CMD ["python", "bot/yahoo.py"]

# aws s3 cp bot/auth s3://usersessiontokens/auth1/ --recursive
# aws s3 cp s3://usersessiontokens/aaron1/ bot/auth --recursive