#!/usr/bin/env python3
import sqlite3 as sqlite


connection = sqlite.connect('database.sql')

cursor = connection.cursor()
make_string = '''
    DROP TABLE `items`;
    CREATE TABLE `items` (
    `index` INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    `item_name` TEXT NOT NULL,
    `ASIN` TEXT NOT NULL,
    `URL` TEXT NOT NULL,
    `actor` TEXT DEFAULT NULL,
    `manufacturer` TEXT DEFAULT NULL,
    `ProductGroup` TEXT
    );
'''
# maybe?:
# url to item
cursor.executescript(make_string)
connection.commit()
connection.close()
