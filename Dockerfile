FROM ruby
# Install python3 and pip for the API, and ruby for anystyle-cli
RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y python3 python3-pip
RUN gem install anystyle-cli

COPY requirements.txt .
COPY app/ /app
COPY model/ /app/model
COPY grobid_client/ /app/grobid_client

RUN pip3 install -r requirements.txt

# Flask is currently always configured for development settings
ENV FLASK_APP=a.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

EXPOSE 5000/tcp

WORKDIR /app

CMD ["flask", "run", "--host=0.0.0.0"]