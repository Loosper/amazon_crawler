#!/usr/bin/env python3
import requests
import json
import xml.etree.ElementTree
import hmac
from lxml import etree
from urllib import parse
from datetime import datetime
from hashlib import sha256
from base64 import b64encode


def load_settings():
    settings = ''
    with open('settings.json', 'r') as info:
        try:
            settings = json.loads(info.read())
        except json.JSONDecodeError:
            print('Invalid settings.')
    return settings


settings = load_settings()

# example input, generated somwhere else
parameters = {
    'Service': 'AWSECommerceService',
    'Operation': 'ItemSearch',
    'AWSAccessKeyId': settings['access_key_id'],
    # 'asdfdsafasd': 'test',
    'AssociateTag': settings['tracking_id'],
    'Keywords': ''
}


def sign_request(query_parameters, secret_key):
    # format of the date:  2014-08-18T12:00:00Z
    current_time = datetime.utcnow()
    query_parameters['Timestamp'] = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    encoded_parameters = [
        parse.urlencode({key: value})
        for key, value in query_parameters.items()
    ]
    encoded_parameters.sort()

    hash_string = (
        'GET\nwebservices.amazon.co.uk\n/onca/xml\n' +
        '&'.join(encoded_parameters)
    ).encode('utf-8')

    hasher = hmac.new(
        secret_key.encode('utf-8'),
        msg=hash_string,
        digestmod=sha256
    ).digest()

    query_parameters['Signature'] = b64encode(hasher).decode()

    return query_parameters


def print_errors(Errors=None: xml):
    for error in Errors:
        print(etree.dump(error))


response = requests.get(
    'http://webservices.amazon.co.uk/onca/xml',
    params=sign_request(parameters, settings['secret_key'])
)
response_data = etree.fromstring(response.text.replace(
    'http://webservices.amazon.com/AWSECommerceService/2011-08-01', ''
))

# print(list(response_data.iter(tag='Arguments')))
for child in response_data.iter('Errors'):
    print_errors()
