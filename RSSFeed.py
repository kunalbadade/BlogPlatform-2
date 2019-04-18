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


class Slash(Extension):
    def get_namespace(self):
        return {"xmlns:slash" : "http://purl.org/rss/1.0/modules/slash/"}

class SlashItem(Serializable):
    def __init__(self, content):
        Serializable.__init__(self)
        self.comments = content

    def publish(self, handler):
        Serializable.publish(self, handler)
        self._write_element("slash:comments", self.comments)



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
    req_article = requests.get('http://localhost:5000/articles/'+ article_id)
    article = req_article.json()
    print(article)
    req_tags = requests.get('http://localhost:5300/get_tags/'+ article_id)
    tags = req_tags.json();
    print(req_tags.json()[0])
    req_comment_count = requests.get('http://localhost:5200/comments/getcommentcount/'+ article_id)
    comment_count = req_comment_count.json()
    print(comment_count)
    items = []
    tags_arr = []
    for i in range (0, len(tags)):
        tags_arr.append(''.join(tags[i]))

    item1 = Item(
        title = article[1],
        link = article[6],
        author = article[1],
        categories = tags_arr,
        pubDate = datetime.datetime.now(),
        extensions = [SlashItem(comment_count)])
    items.append(item1)
    feed = Feed(
        title = "Sample RSS Fee",
        link = "http://www.articles.com/rss",
        description = "Generate RSS Feeds for Articles",
        language = "en-US",
        lastBuildDate = datetime.datetime.now(),
        extensions = [Slash()],
        items = items)

    return (feed.rss())


@app.route("/comment_feed/<article_id>", methods = ['GET'])
def comment_feed(article_id):
    print("in full fee")
    req = requests.get('http://localhost:5000/articles/'+ article_id)
    article = req.json()
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
        title = article[1],
        link = article[6],
        description = article[2],
        language = "en-US",
        lastBuildDate = datetime.datetime.now(),
        items = items)

    return feed.rss()
