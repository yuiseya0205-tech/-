from flask import Flask,request,redirect,render_template_string
import sqlite3

app=Flask(__name__)
DB="techshare.db"

def init():
    con=sqlite3.connect(DB)
    cur=con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT,title TEXT,content TEXT,likes INTEGER DEFAULT 0)")
    cur.execute("CREATE TABLE IF NOT EXISTS comments(id INTEGER PRIMARY KEY AUTOINCREMENT,post_id INTEGER,text TEXT)")
    con.commit()
    con.close()

init()

HTML="""
<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TechShare</title><style>body{font-family:sans-serif;background:#f4f4f4;max-width:1000px;margin:auto;padding:20px}h1{text-align:center}form,.post{background:white;padding:15px;border-radius:10px;margin-bottom:15px}input,textarea,button{width:100%;padding:10px;margin:5px 0}button{cursor:pointer}.comment{background:#eee;padding:8px;margin-top:5px;border-radius:5px}</style></head><body><h1>TechShare</h1><form method="post" action="/post"><input name="username" placeholder="名前" required><input name="title" placeholder="タイトル" required><textarea name="content" rows="6" placeholder="本文" required></textarea><button>投稿</button></form>{% for p in posts %}<div class="post"><h2>{{p[2]}}</h2><p><b>{{p[1]}}</b></p><p>{{p[3]}}</p><form method="post" action="/like/{{p[0]}}"><button>👍 {{p[4]}}</button></form><form method="post" action="/comment/{{p[0]}}"><input name="text" placeholder="コメント"><button>送信</button></form>{% for c in comments[p[0]] %}<div class="comment">{{c}}</div>{% endfor %}</div>{% endfor %}</body></html>
"""

@app.route("/")
def index():
    con=sqlite3.connect(DB)
    cur=con.cursor()
    posts=cur.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    comments={}
    for p in posts:
        comments[p[0]]=[x[0] for x in cur.execute("SELECT text FROM comments WHERE post_id=?",(p[0],)).fetchall()]
    con.close()
    return render_template_string(HTML,posts=posts,comments=comments)

@app.route("/post",methods=["POST"])
def post():
    con=sqlite3.connect(DB)
    cur=con.cursor()
    cur.execute("INSERT INTO posts(username,title,content) VALUES(?,?,?)",(request.form["username"],request.form["title"],request.form["content"]))
    con.commit();con.close()
    return redirect("/")

@app.route("/like/<int:id>",methods=["POST"])
def like(id):
    con=sqlite3.connect(DB)
    cur=con.cursor()
    cur.execute("UPDATE posts SET likes=likes+1 WHERE id=?",(id,))
    con.commit();con.close()
    return redirect("/")

@app.route("/comment/<int:id>",methods=["POST"])
def comment(id):
    text=request.form.get("text","").strip()
    if text:
        con=sqlite3.connect(DB)
        cur=con.cursor()
        cur.execute("INSERT INTO comments(post_id,text) VALUES(?,?)",(id,text))
        con.commit();con.close()
    return redirect("/")

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000)
