from flask import Flask

app = Flask(__name__)
@app.route('/')

def hello():
<<<<<<< HEAD
    return 'Hello, stun!!'
=======
    return 'Hello, stun! + 준원'
>>>>>>> ee5afe40ab4908bf5e19ecc8821eb4bda2142945

if __name__ == '__main__':
    app.run()

