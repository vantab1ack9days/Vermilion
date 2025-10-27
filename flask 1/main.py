from flask import Flask, render_template, request, url_for
import random

app = Flask(__name__)

@app.route("/")
def main():
    nums = []
    for _ in range(1000):
        tmp = '89'
        for __ in range(9):
            symb = str(random.randint(1, 9))
            tmp += symb
        nums.append(tmp)
    return render_template('template.html', nums = nums)


@app.route("/number")
def number():
    num = request.args.get('num')
    return render_template('number.html', num=num)

if __name__ == "__main__":
    app.run(debug=True)