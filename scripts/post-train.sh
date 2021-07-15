#!/bin/bash
# Small shell script to test /parse
curl -X POST -H "Content-Type: text/csv" -H "Overwrite: true" -H "Model_Name: year_models/1851-1900.mod" -d @../model/data/csv/examples-2251.csv http://localhost:5000/train
curl -X POST -H "Content-Type: text/xml" -H "Overwrite: true" -H "Model_Name: year_models/1901-1925.mod" -d @../model/data/xml/train_examples.xml http://localhost:5000/train
