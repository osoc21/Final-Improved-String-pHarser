FROM ruby
# Install python3 and pip for the API, and ruby for anystyle-cli
RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y python3 python3-pip
RUN gem install anystyle-cli

# Set the workdir to /app in the container
WORKDIR /app

COPY requirements.txt .
COPY app/ .

RUN pip3 install -r requirements.txt

# Flask is currently always configured for development settings
ENV FLASK_APP=a.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

EXPOSE 5000/tcp

CMD ["flask", "run"]