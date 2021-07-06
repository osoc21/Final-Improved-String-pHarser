FROM ruby
<<<<<<< HEAD


# Install python3 and pip for the API, and ruby for anystyle-cli
RUN apk update && \ 
    apk add python3 py3-pip ruby ruby-dev
RUN gem install anystyle-cli

=======

# Install python3 and pip for the API, and ruby for anystyle-cli
RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y python3 python3-pip
RUN gem install anystyle-cli
>>>>>>> 617c2b6e35f0adc5186ea7245f8ff5466abd522b

# Set the workdir to /app in the container
WORKDIR /app

COPY requirements.txt .
COPY app/ .

<<<<<<< HEAD
# CMD ["python3", "./docker-tester.py"]

=======
RUN pip3 install -r requirements.txt

CMD ["python3", "./docker-tester.py"]
>>>>>>> 617c2b6e35f0adc5186ea7245f8ff5466abd522b
