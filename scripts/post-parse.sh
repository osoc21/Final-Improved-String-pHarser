#!/bin/bash
# Small shell script to test /parse
curl -X POST -H "Content-Type: text/plain" -d @../model/data/csv/examplesToParse.txt http://localhost:5000/parse/string
