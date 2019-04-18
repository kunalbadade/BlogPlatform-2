from flask import Flask, request, url_for, jsonify, json, g, make_response
import sqlite3
from functools import wraps
import sys
from datetime import datetime

#db_connect = create_engine('sqlite:///blog.db')
DATABASE = '/home/student/Downloads/BlogPlatform2/commentsDb'
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
    cur.execute('SELECT * FROM Comments;')
    results = cur.fetchall()
    return '''<h1>{}<h1>'''.format(results)

#curl --include --verbose --request POST --header 'Content-Type: application/json' --data '{"article_id":"2","comment_content":"Comment1"}' http://localhost:5000/new_comment
@app.route('/new_comment', methods = ['POST', 'GET'])
def api_new_comment():
    statusCode = 0
    data = None
    CommentId = None
    lastCommentId = 1
    date = datetime.now()
    if request.method == 'POST':
        data = request.get_json()
        article_id = data['article_id']
        comment_content = data['comment_content']
        #comment_id = data['comment_id']
        cur = get_db().cursor()
        if not request.authorization:
             user_name = "Anonymous Coward"
        else:
            user_name = request.authorization["username"]
        try:
            cur.execute('SELECT MAX(comment_id) FROM comments;')
            lastCommentId = cur.fetchone()[0]
            if lastCommentId != None:
               lastCommentId += 1
            cur.execute('INSERT INTO comments (comment_id, comment_content, article_id, user_name, createstamp) VALUES (?,?,?,?,?);',(lastCommentId, comment_content, article_id, user_name, date))
            get_db().commit()
            if cur.rowcount >= 1:
                statusCode = 1
            else:
                statusCode = 0
        except:
            get_db().rollback()
            statusCode = 0
        finally:
            if statusCode == 1:
                url = 'http://127.0.0.1/new_comment/' + str(lastCommentId)
                resp = jsonify(data)
                resp.status_code = 201
                resp.headers['Link'] = url
                return resp
            else:
                return jsonify(message = "Failed"),409

#curl --request DELETE --header 'Content-Type: application/json' http://localhost:5000/comments/123
@app.route('/comments/<comment_id>', methods = ['DELETE'])
def api_delete_comment(comment_id):
    if request.method == 'DELETE':
        #statusCode:bool = False
        statusCode = 0
        cur = get_db().cursor()
        try:
            cur.execute('DELETE FROM comments WHERE comment_id = ?', (comment_id,))
            get_db().commit()
            if cur.rowcount >= 1:
                statusCode = 1
        except:
            get_db().rollback()
            statusCode = 0
        finally:
            if statusCode == 1:
                return jsonify(message = "Passed"),200
            else:
                return jsonify(message = "Failed"),409

#curl --include --verbose --request GET --header 'Content-Type: application/json' http://localhost:5000/comments/getcommentcount/2
@app.route('/comments/getcommentcount/<article_id>', methods = ['GET'])
def api_count_comment(article_id):
    statusCode = 0
    cur = get_db().cursor()
    try:
        cur.execute('SELECT count(*) FROM comments WHERE article_id = ?', (article_id,))
        CommentRecord = cur.fetchone()
        if not CommentRecord == None:
               statusCode = 1
        else:
            statusCode = 0
    except:
        statusCode = 0
    finally:
       if statusCode == 1:
          resp = jsonify(CommentRecord)
          resp.status_code = 200
          return resp
       else:
          return jsonify(message = "Failed"),409

#curl --include --verbose --request GET --data '{"n":"2"}' --header 'Content-Type: application/json' http://localhost:5300/comments/getncomments/1
@app.route('/comments/getncomments/<article_id>', methods = ['GET'])
def api_n_comment(article_id):
    statusCode = 0
    data = request.get_json()
    n = data['n']
    cur = get_db().cursor()
    try:
        cur.execute('SELECT comment_content, createstamp FROM (SELECT comment_content, createstamp FROM comments where article_id = ?) ORDER BY createstamp DESC LIMIT ?',(article_id,n))
        results = cur.fetchall()
        if results != None:
           statusCode = 1
        else:
            statusCode = 0
    except:
        statusCode = 0
    finally:
        if statusCode == 1:
           resp = jsonify(results)
           resp.status_code = 200
           return resp
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
#class Article(Resource):
#    def get(self, name):
#        conn = db_conneect .connnect()
#        for article in articles:
#            if(name == user["name"]):
#                return article, 200
#        return "Article not found, 404
