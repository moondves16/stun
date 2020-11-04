from flask import Flask

app = Flask(__name__)
@app.route('/')

def hello():
    return 'Hello, stun!!'
    return 'Hello, stun! + 준원'
    return 'Hello, stun! + 환'

if __name__ == '__main__':
    app.run()