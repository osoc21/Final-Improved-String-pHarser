#!/bin/bash
# Small shell script to test /parse
curl -X POST -H "Content-Type: text/csv" -d @../model/data/csv/examples-2251.csv http://localhost:5000/train
curl -X POST -H "Content-Type: text/xml" -d @../model/data/xml/train_examples.xml http://localhost:5000/train
