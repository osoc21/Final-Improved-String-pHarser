import csv
import sys
import argparse

'''
Example usage: python3 examples.csv converted-examples.xml
'''
parser = argparse.ArgumentParser(description='Convert CSV file to XML file.')
parser.add_argument('input_file', metavar='N', type=str, nargs='+',
                    help='The input CSV file.')
parser.add_argument('output_file', metavar='N', type=str, nargs='+',
                    help='The output XML file.')

input_file = sys.argv[1]
output_file = sys.argv[2]

citations = []

with open(input_file,  encoding="utf-8") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    column_names = []
    for row in csv_reader:
        if line_count == 0:
            for column_name in row:
                column_names.append(column_name)
            line_count += 1
        else:
            citation = {}
            for i in range(len(row)):
                citation[column_names[i]] = row[i]
            citations.append(citation)
            line_count += 1

import xml.etree.ElementTree as ET

# Create xml structure
data = ET.Element('dataset')
for citation in citations:
    # Each citation is in a sequence tag
    items = ET.SubElement(data, 'sequence')
    # For each field of the citation add a xml tag and set the text
    for field in citation:
        # No need to output the string field
        if field != "String" and citation[field] != "":
            item1 = ET.SubElement(items, field)
            item1.text = citation[field]

# create a new XML file with the results
xmldata = ET.tostring(data)
xmlfile = open(output_file, "wb")
xmlfile.write(xmldata)