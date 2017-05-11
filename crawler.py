#!/usr/bin/env python3.6
import requests
import json
import hmac
import sqlite3 as sqlite
import xml.etree.ElementTree as etree
import time
# from xml.dom import minidom
# may be easier to use
from re import sub
from urllib import parse
from datetime import datetime
from hashlib import sha256
from base64 import b64encode


class AmazonAPIHandler:
    def __init__(self, settings, extra_parameters={}):
        self.settings = settings
        self.parameters = {
            'Service': 'AWSECommerceService',
            'AWSAccessKeyId': self.settings['access_key_id'],
            'AssociateTag': self.settings['tracking_id'],
            **extra_parameters
        }

    def _print_errors(self):
        for error in self.response.findall('Items/Request/Errors/'):
            # use logging instead of simple prints
            etree.dump(error)

        for error in self.response.findall('Error'):
            etree.dump(error)

    def _sign_request(self):
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
        self._sign_request()
        response = requests.get(
            'http://webservices.amazon.co.uk/onca/xml',
            params=self.parameters
        )

        response_data = etree.fromstring(
            sub(' xmlns="[^"]+"', '', response.text, count=1)
        )

        self.response = response_data

        # etree.dump(response_data)
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


# BrowseNodeLookup
# this loads all subelements as well. Might want to control that
# Also is there any use in mapping parents to children?
def load_browse_node(node_id: int):
    request = AmazonAPIHandler(
        settings, {'Operation': 'BrowseNodeLookup', 'BrowseNodeId': node_id}
    )

    query = '''
    INSERT OR REPLACE INTO `browse_nodes`
        (`node_id`, `Name`, `has_children`)
    VALUES
        (?, ?, ?);
    '''
    children_number = 0
    response = request.send_request()
    # etree.dump(response)
    for child in response.findall(
        'BrowseNodes/BrowseNode/Children/BrowseNode'
    ):
        load_browse_node(child.find('BrowseNodeId').text)
        # etree.dump(child)
        children_number += 1

    # if children_number != 0:

    data = (
        node_id,
        response.find('BrowseNodes/BrowseNode/Name').text,
        children_number
    )
    cursor.execute(query, data)

    # commit here or not?


# ItemSearch
def get_items(parameters):
    request = AmazonAPIHandler(settings, parameters)

    response = request.send_request()
    query = '''
    INSERT OR IGNORE INTO `items`
    ({})
    VALUES ({}); -- (?, ?, ?, ?, ?)
    '''

    for item in response.findall('Items/Item'):
        # etree.dump(item)
        values = {
            'ASIN': item.find('ASIN').text,
            'DetailPageURL': item.find('DetailPageURL').text,
            **{param.tag: param.text for param in item.find('ItemAttributes')}
        }

        columns = ', '.join(values.keys())
        placeholder = ':'+', :'.join(values.keys())

        # print(json.dumps(values))
        cursor.execute(query.format(columns, placeholder), values)


# put this in a thread and wait 1 second
# ~0.17 is the fastest ItemSearch
# ~0.13 is that of BrowseNodeLookup
def api_timeout_handler(executer):
    start = time.time()
    executer()
    print(time.time() - start)


settings = load_settings()

connection = sqlite.connect('database.sql')
cursor = connection.cursor()


# ItemLookup for price
# None

get_items({
    'Operation': 'ItemSearch', 'Keywords': 'SSD',
    'SearchIndex': 'PCHardware', 'MinPercentageOff': 20
})

# load_browse_node(560800)

connection.commit()

cursor.execute(
    '''
    SELECT `node_id`, `Name`, `has_children`
    FROM `browse_nodes`
    WHERE `has_children` = 0;
    '''
)
# cursor.execute('SELECT `Title` FROM `items`')

# print(json.dumps(cursor.fetchall()))
