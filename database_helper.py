#!/usr/bin/env python3
# Copyright (c) 2016 Aliya Iskhakova <iskhakova.alija@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sqlite3
import pickle
import sys
import os


def init_database():

    conn = sqlite3.connect(fetch_database_path())
    cur = conn.cursor()

    cur.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name            TEXT UNIQUE,
        reviewer_rate   INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS cache (
        id       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        url      TEXT,
        response BLOB
    );
    ''')
    conn.commit()
    conn.close()


def increment_user_rating(user):
    conn = sqlite3.connect(fetch_database_path())
    cur = conn.cursor()

    cur.execute('''UPDATE users SET reviewer_rate = reviewer_rate + 1  WHERE name = ?''', (user,))
    print("User's rating updated: ", user)

    if cur.rowcount == 0:  # there is no such user in db
        cur.execute('''INSERT INTO users (name, reviewer_rate) VALUES ( ?, ? )''', (user, 1))
        print ('User added to db: ', user)

    conn.commit()
    conn.close()


def cache_response(url, etag):
    conn = sqlite3.connect(fetch_database_path())
    cur = conn.cursor()

    pdata = pickle.dumps(etag, pickle.HIGHEST_PROTOCOL)
    cur.execute('''UPDATE cache SET response = ?  WHERE url = ?''', (sqlite3.Binary(pdata), url))

    if cur.rowcount == 0:  # there is no cached response with that url
        cur.execute('''INSERT INTO cache (url, response) VALUES ( ?, ? )''', (url, sqlite3.Binary(pdata)))

    conn.commit()
    conn.close()


def fetch_cached_response(url):
    conn = sqlite3.connect(fetch_database_path())
    cur = conn.cursor()

    cur.execute('''SELECT response FROM cache WHERE url = ?''', (url,))
    row = cur.fetchone()
    result = pickle.loads(row[0]) if row is not None else None

    conn.commit()
    conn.close()
    return result


def remove_response(url):
    conn = sqlite3.connect(fetch_database_path())
    cur = conn.cursor()

    cur.execute('''DELETE FROM cache WHERE url = ?''', (url,))
    conn.commit()
    conn.close()

def fetch_user_rating(user):
    conn = sqlite3.connect(fetch_database_path())
    cur = conn.cursor()

    cur.execute('''SELECT reviewer_rate FROM users WHERE name = ?''', (user,))
    result = cur.fetchone()
    if result is not None:
        result = int(result[0])

    conn.commit()
    conn.close()
    return result if result is not None else 0

def fetch_database_path():
    project_path = sys.path[0]
    db_folder = project_path  + '/data'

    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
    db_path = db_folder + '/lottery.sqlite'

    return db_path
