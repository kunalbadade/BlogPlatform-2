from flask import Flask, request, url_for, jsonify, json, g
'''from flask_restful import Api, Resource, reqparse'''
import sqlite3
import sys
from datetime import datetime
from functools import wraps
from passlib.hash import pbkdf2_sha256

#db_connect = create_engine('sqlite:///blog.db')
DATABASE = '/home/student/Desktop/github/BlogPlatform2/Blog_Database.db'
app = Flask(__name__)
#api = Api(app)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    cur = get_db().cursor()
    cur.execute('SELECT * FROM tags;')
    results = cur.fetchall()
    return '''<h1>{}<h1>'''.format(results)

#curl --include -u kunal:kunal --verbose --request POST --header 'Content-Type: application/json' --data '{"tags":["tag3","tag4"]}' http://localhost:5100/new_tag/1
@app.route('/new_tag/<article_id>', methods = ['POST'])
def api_new_tag(article_id):
    print("parag here")
    data = None
    articleId = None
    article_url = None
    tagData = None
    lastRowId = None
    newTagId = None
    statusCode = None
    print(article_id)
    print(request.get_json())
    if request.method == 'POST':
        statusCode:bool = False
        cur = get_db().cursor()
        try:
            data = request.get_json()
            tags = request.get_json()['tags']
            article_url = 'http://127.0.0.1:5000/articles/' + str(article_id)
            for tag in tags:
                cur.execute('SELECT * from tags where tag_name = ? and article_id = ?',(tag, article_id))
                results = cur.fetchall()
                if len(results) == 0:
                    cur.execute('insert into tags (tag_name, article_id, article_url) values(?,?,?);',(tag, article_id, article_url,))
                    newTagId = cur.lastrowid
                    get_db().commit()
                    statusCode = True
        except:
            get_db().rollback()
            statusCode = False
        finally:
            if statusCode:
                url = 'http://127.0.0.1:5100/tags/' + str(newTagId)
                resp = jsonify(data)
                resp.status_code = 201
                resp.headers['Link'] = url
                return resp
            else:
                return jsonify(message="Failed"),409

#curl -u kunal:kunal --include --verbose --request DELETE --header 'Content-Type: application/json' http://localhost:5100/remove_tags/<article_id>
@app.route('/remove_tags/<article_id>', methods = ['DELETE'])
def api_remove_tags(article_id):
    cur = get_db().cursor()
    status_code :bool= False
    try:
        cur.execute("DELETE FROM tags WHERE article_id = ?",(article_id,))
        get_db().commit()
        if cur.rowcount >= 1:
            status_code = True
    except:
        get_db().rollback()
        status_code = False
    finally:
        if status_code:
            return jsonify(message="Tags Deleted successfully"), 200
        else:
            return jsonify(message="Tags Deletion Failed"), 409

#curl -u kunal:kunal --include --verbose --request GET --header 'Content-Type: application/json' http://localhost:5100/get_articles_for_tag/<tag_id>
@app.route('/get_articles_for_tag/<tag_id>', methods = ['GET'])
def api_get_articles_for_tag(tag_id):
    cur = get_db().cursor()
    no_tags_found:bool = False
    status_code:bool = False
    try:
        print("here")
        cur.execute('SELECT article_url from tags where tag_id = ?',(tag_id,))
        articles = cur.fetchall()
        print(len(articles))
        if len(articles) != 0:
            status_code = True
        else:
            no_tags_found = True
    except:
        get_db().rollback()
        status_code = False
    finally:
        if status_code:
            resp = jsonify(articles)
            resp.status_code = 200
            return resp
        else:
            if no_tags_found == True:
                return jsonify(message="No Articles Found"), 404
            else:
                return jsonify(message="Failed"), 409

#curl -u kunal:kunal --include --verbose --request GET --header 'Content-Type: application/json' http://localhost:5100/get_tags/<article_id>
@app.route('/get_tags/<article_id>', methods = ['GET'])
def api_get_tags(article_id):
    cur = get_db().cursor()
    no_tags_found = False
    status_code = False
    try:
        print("here wjo")
        cur.execute('SELECT article_id FROM tags WHERE article_id = ?',(article_id,))
        print("kay zala")
        isArticleIDpresent = cur.fetchall()
        if isArticleIDpresent != None:
            print("ata ithe")
            cur.execute('SELECT tag_name FROM tags WHERE article_id = ?',(article_id,))
            tags = cur.fetchall()
            if len(tags) != 0:
                status_code = True
            else:
                no_tags_found = True
        else:
            status_code = False
    except:
        get_db().rollback()
        status_code = False
    finally:
        if status_code:
            resp = jsonify(tags)
            resp.status_code = 200
            return resp
        else:
            if no_tags_found == True:
                return jsonify(message="No Tags Found"), 404
            else:
                return jsonify(message="Failed"), 404

@app.errorhandler(404)
def not_found(error=None):
    message = {
    'status' : 404,
    'message': 'Not found : '+ request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return 404

if __name__ == '__main__':
    app.run(debug = True)
#class Article(Resource):
#    def get(self, name):
#        conn = db_conneect .connnect()
#        for article in articles:
#            if(name == user["name"]):
#                return article, 200
#        return "Article not found, 404
