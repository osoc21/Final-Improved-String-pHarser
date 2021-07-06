import requests
import os

"""Test the docker installation by running the following
    docker build -t fish .
    docker run fish python3 docker-tester.py
"""

"""This print should return 200. This will prove that the following things work:
    - Internet connectivity through a google request
    - HTTPS requests
    - Installing python requirements through pip
      (as this should've been done in the docker build)
"""
print(requests.get("https://www.google.com").status_code)

"""This print should return the help of anystyle-cli. This will prove that the following things work:
    - The ruby installation
    - The anystyle-cli installation
    - The connectivity between python and anystyle-cli
"""
print(os.system("anystyle"))
