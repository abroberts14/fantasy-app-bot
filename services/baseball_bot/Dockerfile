FROM python:3.11-buster

RUN mkdir app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.


COPY  . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#RUN aws s3 cp s3://usersessiontokens/auth${user_id}/ bot/auth --recursive
CMD ["python3", "bot.py"]

# aws s3 cp bot/auth s3://usersessiontokens/auth1/ --recursive
# aws s3 cp s3://usersessiontokens/aaron1/ bot/auth --recursive