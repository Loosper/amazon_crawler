#!/usr/bin/env python3
import sqlite3 as sqlite


connection = sqlite.connect('database.sql')

cursor = connection.cursor()
make_string = '''
    DROP TABLE IF EXISTS `items`;
    CREATE TABLE `items` (
    `Title` TEXT NOT NULL,
    `Price` INTEGER DEFAULT NULL,
    `ASIN` TEXT PRIMARY KEY,
    `DetailPageURL` TEXT NOT NULL,
    `actor` TEXT DEFAULT NULL,
    `Manufacturer` TEXT DEFAULT NULL,
    `ProductGroup` TEXT,
    `Creator`
    );
    --`date_added`

    DROP TABLE IF EXISTS 'browse_nodes';
    CREATE TABLE `browse_nodes` (
        `node_id` INTEGER PRIMARY KEY,
        `Name` TEXT NOT NULL,
        `has_children` INTEGER DEFAULT NULL,
        `valid` INTEGER DEFAULT NULL
    )
'''
# maybe?:
# url to item
cursor.executescript(make_string)
connection.commit()
connection.close()
