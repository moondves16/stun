import flask
import pymysql
import OpenSSL
from flask import Flask
from flask import render_template


app = Flask(__name__)
@app.route("/")
def hello():
    return "<h1>Jaaa</h1>"

@app.route('/<user>')
def test(user):
    return user

@app.route('/test')
def get_html():
   return render_template('view.html', aa ='전달데이터', bb="1234", cc =[1,2,3])

@app.route('/hello/<user>')
def hello_name(user):
   return render_template('view.html', data=user)

@app.route("/index")
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
