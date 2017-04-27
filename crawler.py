#!/usr/bin/env python3
import requests
import json
import hmac
import sqlite3 as sqlite
# from lxml import etree
import xml.etree.ElementTree as etree
from urllib import parse
from datetime import datetime
from hashlib import sha256
from base64 import b64encode


class AmazonAPIHandler:
    def __init__(self, settings, extra_parameters={}):
        self.settings = settings
        self.parameters = {
            'Service': 'AWSECommerceService',
            'Operation': 'ItemSearch',
            'AWSAccessKeyId': self.settings['access_key_id'],
            'AssociateTag': self.settings['tracking_id'],
            **extra_parameters
        }

    def _print_errors(self):
        for error in self.response.findall('Items/Request/Errors/'):
            # use logging instead of simple prints
            etree.dump(error)

    def sign_request(self):
        # format of the date:  2014-08-18T12:00:00Z
        current_time = datetime.utcnow()
        self.parameters['Timestamp'] = current_time.strftime(
            '%Y-%m-%dT%H:%M:%SZ'
        )

        encoded_parameters = [
            parse.urlencode({key: value}, quote_via=parse.quote)
            for key, value in self.parameters.items()
        ]
        encoded_parameters.sort()
        # print(encoded_parameters)

        hash_string = (
            'GET\nwebservices.amazon.co.uk\n/onca/xml\n' +
            '&'.join(encoded_parameters)
        ).encode('utf-8')

        hasher = hmac.new(
            self.settings['secret_key'].encode('utf-8'),
            msg=hash_string,
            digestmod=sha256
        ).digest()

        self.parameters['Signature'] = b64encode(hasher).decode()

    def send_request(self):
        self.sign_request()
        response = requests.get(
            'http://webservices.amazon.co.uk/onca/xml',
            params=self.parameters
        )
        response_data = etree.fromstring(response.text.replace(
            'http://webservices.amazon.com/AWSECommerceService/2011-08-01', ''
        ))
        self.response = response_data

        # print(response.text)
        self._print_errors()

        # either return or assign to self, not sure which is needed
        return response_data


def load_settings():
    settings = ''
    with open('settings.json', 'r') as info:
        try:
            settings = json.loads(info.read())
        except json.JSONDecodeError:
            print('Invalid settings.')
    return settings


settings = load_settings()

request = AmazonAPIHandler(settings, {
    'Keywords': 'SSD', 'SearchIndex': 'PCHardware', 'MinPercentageOff': '20'
})
# print(request.send_request())
# etree.dump(request.send_request())
response = request.send_request()

connection = sqlite.connect('database.sql')
cursor = connection.cursor()
query = '''INSERT INTO `items`
    (`ASIN`, `URL`, `ProductGroup`, `manufacturer`,`item_name`)
    VALUES (?, ?, ?, ?, ?)
'''

for item in response.findall('Items/Item'):
    values = (
        item.find('ASIN').text,
        item.find('DetailPageURL').text,
        *(param.text for param in item.find('ItemAttributes'))
    )
    cursor.execute(query, values)

cursor.execute('SELECT `item_name` FROM `items`')
print(cursor.fetchall())
# etree.dump(response)
