#!/usr/bin/env python3
import requests
import json
import hmac
from urllib import parse
from datetime import datetime
from hashlib import sha256
from base64 import b64encode


def load_settings():
    settings = ''
    with open('settings.json', 'r') as info:
        settings = json.loads(info.read())

    return settings


settings = load_settings()

# example input, generated somwhere else
parameters = {
    'Service': 'AWSECommerceService',
    'AWSAccessKeyId': settings['access_key_id'],
    # 'asdfdsafasd': 'test',
    'AssociateTag': settings['tracking_id']
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
        'GET\nwebservices.amazon.com\n/onca/xml\n' +
        '&'.join(encoded_parameters)
    ).encode('utf-8')

    hasher = hmac.new(
        secret_key.encode('utf-8'),
        msg=hash_string,
        digestmod=sha256
    ).digest()

    query_parameters['Signature'] = b64encode(hasher).decode()

    return query_parameters


# print(load_settings())
