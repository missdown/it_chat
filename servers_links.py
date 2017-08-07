from flask import Flask
import hashlib

app = Flask(__name__)
data ="fasdfa".encode()
print(hashlib.sha1(data).hexdigest())

@app.route('/links', methods=['GET', 'POST'])
def links():
    return "1"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)