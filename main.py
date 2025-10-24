# main.py

from flask import Flask, request

app = Flask(__name__)

@app.route("/calc")
def calculator():
    a = int(request.args.get('a'))
    b = int(request.args.get('b'))
    op = request.args.get('op')
    if op=='add':
        return f'Result is {a+b}'
    elif op=='diff':
        return f'Result is {a-b}'
    if op=='mult':
        return f'Result is {a*b}'
    if op=='sub':
        return f'Result is {a/b}'
    



if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host='10.42.0.1', port=5000)