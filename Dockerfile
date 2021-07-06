# Alternatively, ruby:alpine can also be used
FROM alpine:3


# Install python3 and pip for the API, and ruby for anystyle-cli
RUN apk update && \ 
    apk add python3 py3-pip ruby

#RUN gem install anystyle-cli


# Set the workdir to /app in the container
WORKDIR /app


COPY app/ .

# CMD ["python3", "./docker-tester.py"]
