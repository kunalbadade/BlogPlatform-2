sqlite3 ArticlesDb.db

CREATE TABLE articles( article_is INTEGER PRIMARY KEY,
		       article_title TEXT NOT NULL,
		       article_content TEXT NOT NULL,
		       createstamp TIMESTAMP,
		       updatestamp TIMESTAMP,
		       url TEXT NOT NULL,
				 	 user_name TEXT NOT NULL);

sqlite3 CommentsDb.db

CREATE TABLE comments(comment_id INTEGER NOT NULL PRIMARY KEY,
		      comment_content TEXT ,
   		      createstamp TIMESTAMP,
   		      updatestamp TIMESTAMP,
   		      article_id INTEGER NOT NULL,
   		      user_name TEXT NOT NULL);

sqlite3 TagsDb.db

CREATE TABLE tags( tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
			   					 tag_name TEXT NOT NULL
									 article_id INTEGER
								 	 article_url TEXT);

sqlite3 UsersDb.db

CREATE TABLE users(user_id INTEGER PRIMARY KEY,
		   user_name TEXT NOT NULL,
		   password TEXT NOT NULL,
		   active_status INTEGER NOT NULL);
