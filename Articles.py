from flask import Flask, request, url_for, jsonify, json, g, make_response
import sqlite3
import sys
from datetime import datetime
from functools import wraps
from passlib.hash import pbkdf2_sha256

#db_connect = create_engine('sqlite:///blog.db')
DATABASE = '/home/student/github/articlesDb'
app = Flask(__name__)
#api = Api(app)
isAuthenticated = True
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
    cur.execute('SELECT * FROM articles;')
    results = cur.fetchall()
    return '''<h1>{}<h1>'''.format(results)

def api_root():
    return "Welcome"

#curl -u kunal:kunal --include --verbose --request POST --header 'Content-Type: application/json' --data '{"article_content":"MyContent","article_title":"MyTitle","tags":["tag1","tag2"]}' http://localhost:5000/new_article
#curl -u kunal:kunal --include --verbose --request POST --header 'Content-Type: application/json' --data '{"article_content":"MyNewContent","article_title":"MyNewTitle","tags":["tag1","tag3"]}' http://localhost:5000/new_article
@app.route('/new_article', methods = ['POST','GET'])
def api_new_article():
    data = None
    articleId = None
    lastRowArticleId = 1
    username = request.authorization['username']
    if request.method == 'POST':
        statusCode:bool = False
        cur = get_db().cursor()
        try:
            data = request.get_json()
            article_content = data['article_content']
            article_title = data['article_title']
            cur.execute('SELECT MAX(article_id) FROM articles;')
            lastRowArticleId = cur.fetchone()[0]
            if lastRowArticleId != None:
                lastRowArticleId += 1
            url = 'http://127.0.0.1/articles/' + str(lastRowArticleId)
            now = datetime.now()
            cur.execute('INSERT INTO articles (article_title, article_content, user_name, createstamp, updatestamp, url) VALUES (?,?,?,?,?,?);',(article_title, article_content, username, now, now, url))
            articleId = cur.lastrowid
            get_db().commit()
            statusCode = True
        except:
            get_db().rollback()
            statusCode = False
        finally:
            if statusCode:
                url = 'http://127.0.0.1/articles/' + str(articleId)
                resp = jsonify(data)
                resp.status_code = 201
                resp.headers['Link'] = url
                return resp
            else:
                return jsonify(message="Failed"),409

#curl -u kunal:kunal --include --verbose --request GET --header 'Content-Type: application/json' --data '{"article_content":"MyNewContent","article_title":"MyNewTitle","tags":["tag1","tag3"]}' http://localhost:5000/articles/2
@app.route('/articles/<article_id>', methods = ['GET'])
def api_get_article(article_id):
    if request.method == 'GET':
        statusCode:bool = False
        notFound:bool = False
        cur = get_db().cursor()
        try:
            cur.execute('SELECT * FROM articles WHERE article_id = ?', (article_id,))
            articleRecord = cur.fetchone()
            if articleRecord != None:
                statusCode = True
            else:
                notFound = True
        except:
            get_db().rollback()
            statusCode = False
        finally:
            if statusCode:
                resp = jsonify(articleRecord)
                resp.status_code = 200
                return resp
            else:
                if notFound:
                    return jsonify(message="Article record not found for the given id"),404
                else:
                    return jsonify(message="Failed"),409

#curl -u kunal:kunal --include --verbose --request GET --header 'Content-Type: application/json' --data '{"n":"3"}' http://localhost:5000/articles
@app.route('/articles', methods = ['GET'])
def api_get_n_article():
    if request.method == 'GET':
        statusCode:bool = False
        notFound:bool = False
        cur = get_db().cursor()
        try:
            data = request.get_json()
            n = data['n']
            cur.execute('SELECT * FROM ( \
            SELECT * FROM articles ORDER BY updatestamp DESC LIMIT ? )\
            ORDER BY updatestamp DESC', (n,))
            articleRecord = cur.fetchall()
            if articleRecord != None:
                statusCode = True
            else:
                notFound = True
        except:
            get_db().rollback()
            statusCode = False
        finally:
            if statusCode:
                resp = jsonify(articleRecord)
                resp.status_code = 200
                return resp
            else:
                if notFound:
                    return jsonify(message="Article records not found"),404
                else:
                    return jsonify(message="Failed"),409
#curl -u kunal:kunal --include --verbose --request GET --header 'Content-Type: application/json' --data '{"n":"3"}' http://localhost:5000/articles
@app.route('/articles_metadata', methods = ['GET'])
def api_get_article_metadata():
    if request.method == 'GET':
        statusCode:bool = False
        notFound:bool = False
        cur = get_db().cursor()
        try:
            data = request.get_json()
            n = data['n']
            cur.execute('SELECT * FROM ( \
            SELECT article_title, article_content, user_name, createstamp, updatestamp, url FROM articles ORDER BY updatestamp DESC LIMIT ? )\
            ORDER BY updatestamp DESC', (n,))
            articleRecord = cur.fetchall()
            if articleRecord != None:
                statusCode = True
            else:
                notFound = True
        except:
            get_db().rollback()
            statusCode = False
        finally:
            if statusCode:
                resp = jsonify(articleRecord)
                resp.status_code = 200
                return resp
            else:
                if notFound:
                    return jsonify(message="Article records not found"),404
                else:
                    return jsonify(message="Failed"),409

#curl -u kunal:kunal --include --verbose --request PUT --header 'Content-Type: application/json' --data '{"article_title":"UpdatedTitle","article_content":"UpdatedContent"}' http://localhost:5000/articles/5
@app.route('/articles/<article_id>', methods = ['PUT'])
def api_update_article(article_id):
    if request.method == 'PUT':
        statusCode:bool = False
        cur = get_db().cursor()
        try:
            data = request.get_json()
            article_content = data['article_content']
            article_title = data['article_title']
            now = datetime.now()
            cur.execute('UPDATE articles SET article_title = ?, article_content = ?, updatestamp = ? where article_id = ?',(article_title, article_content, now, article_id))
            get_db().commit()
            if cur.rowcount >= 1:
                statusCode = True
        except:
            get_db().rollback()
            statusCode = False
        finally:
            if statusCode:
                url = 'http://127.0.0.1/articles/' + str(article_id)
                resp = jsonify(data)
                resp.status_code = 200
                resp.headers['Link'] = url
                return resp
            else:
                return jsonify(message="Failed"),409

#curl -u kunal:kunal --include --verbose --request DELETE --header 'Content-Type: application/json' --data '{"article_title":"UpdatedTitle","article_content":"UpdatedContent"}' http://localhost:5000/articles/6
@app.route('/articles/<article_id>', methods = ['DELETE'])
def api_delete_article(article_id):
    if request.method == 'DELETE':
        statusCode:bool = False
        cur = get_db().cursor()
        try:
            cur.execute('DELETE FROM articles WHERE article_id = ?', (article_id,))
            get_db().commit()
            if cur.rowcount >= 1:
                statusCode = True
        except:
            get_db().rollback()
            statusCode = False
        finally:
            if statusCode:
                return jsonify(message = "Record Deleted Successfully"),200
            else:
                return jsonify(message = "Failed"),409

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
    app.run(debug=True)
