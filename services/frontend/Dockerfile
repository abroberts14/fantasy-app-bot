FROM node:lts-alpine
ENV HOST=0.0.0.0

WORKDIR /app

ENV PATH /app/node_modules/.bin:$PATH

RUN npm install @vue/cli@5.0.8 -g

COPY package.json .
COPY package-lock.json .
RUN npm install
# copy project files and folders to the current working directory (i.e. 'app' folder)
COPY . .
EXPOSE 5173


#CMD ["npm", "run", "dev"]
