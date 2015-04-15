#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import csv
import argparse
import json

from lxml import etree


# CSVFILE = '/home/ramp/tmp/CLOUD_DBAAS_from_09.03.2015_to_16.03.2015.csv'

class Printer:
    def __init__(self):
        self.output = []

    def outfield(self, text):
        if text:
            self.output.append(text)

    def commit(self):
        sep = '|'
        print (sep.join(self.output))
        self.output = []
        return True

    def commitIfFieldCount(self, count):
        if len(self.output) == count:
            return self.commit()
        else:
            self.output = []
            return False

    def outnode(self, node):
        for value in node.values():
            self.outfield(value)

        if node.text:
            if self._isJson(node.text):
                self.outJsonNode(None, json.loads(node.text))
            else:
                self.outfield(node.text)

        for child in node:
            self.outnode(child)

    def outheader(self, node):
        for key in node.keys():
            self.outfield(key)

        if node.text:
            if self._isJson(node.text):
                self.outJsonHeader(None, json.loads(node.text))
            else:
                self.outfield(etree.QName(node.tag).localname)

        for child in node:
            self.outheader(child)

    def outJsonNode(self, key, text):
        if type(text) == dict:
            for k, value in text.items():
                self.outJsonNode(k, value)
        else:
            self.outfield(str(text))

    def outJsonHeader(self, key, text):
        if type(text) == dict:
            for k, value in text.items():
                self.outJsonHeader(k, value)
        else:
            self.outfield(key)        

    def _isJson(self, text):
        return text[0] == '{' and text[-1] == '}'

def main():
    is_header_printed = False
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', default=sys.stdin)
    parser.add_argument('--fc', type=int)
    args = parser.parse_args()

    filename = args.filename
    fieldcount = args.fc


    printer = Printer()
    with open(filename) as csvfile:
        # TODO: miss first line if it is not a header!
        header = csvfile.readline()
        delimiter = csv.Sniffer().sniff(header).delimiter
        if delimiter not in [',',';','\t','|','^']:
            delimiter = '\t'

        for line in csvfile:
            _, rawxml, _ = line.split(delimiter)
            root = etree.fromstring(rawxml.encode())
            if not is_header_printed:
                printer.outheader(root)
                if fieldcount:
                    is_header_printed = printer.commitIfFieldCount(fieldcount)
                else:
                    is_header_printed = printer.commit()

            printer.outnode(root)
            if fieldcount:
                printer.commitIfFieldCount(fieldcount)
            else:
                printer.commit()

if __name__ == '__main__':
    sys.exit(main())