#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from flask import Flask, request, url_for, jsonify, json, g, make_response
import sqlite3
import sys
from datetime import datetime
from functools import wraps
from passlib.hash import pbkdf2_sha256
import datetime
from rfeed import *


app = Flask(__name__)

@app.route("/summary_feed", methods = ['GET'])
def summary_feed():
    r = requests.get('http://localhost:5000/articles', json = {"n" : "10"})
    arr = r.json()
    items = []
    for i in range(0, 10):
        item1 = Item(
            title = arr[i][1],
            link = arr[i][6],
            author = arr[i][1],
            pubDate = datetime.datetime.now())
        items.append(item1)

    feed = Feed(
        title = "Sample RSS Feed",
        link = "http://www.articles.com/rss",
        description = "Generate RSS Feeds for Articles",
        language = "en-US",
        lastBuildDate = datetime.datetime.now(),
        items = items)

    return (feed.rss())

@app.route("/full_feed/<article_id>", methods = ['GET'])
def full_feed(article_id):
    print("in full fee")
    items = []
    r = requests.get('http://localhost:5200/comments/getncomments/'+ article_id, json = {"n" : "3"})
    arr = r.json()
    for i in range(0, len(r.json())):
        date_time_str = str(arr[i][1])
        '''date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')'''
        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')

        item1 = Item(
            title = arr[i][0],
            description = "description",
            comments = arr[i][0],
            pubDate = date_time_obj)
        items.append(item1)

    feed = Feed(
        title = "Sample RSS Feed",
        link = "http://www.articles.com/rss",
        description = "Generate RSS Feeds for Articles",
        language = "en-US",
        lastBuildDate = datetime.datetime.now(),
        items = items)

    return feed.rss()
