from flask import Flask, render_template, request, url_for
import random

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == 'POST':
        input_num = request.form['phone_num']
        return number(input_num)
    else:
        nums = []
        for _ in range(1000):
            tmp = '89'
            for __ in range(9):
                symb = str(random.randint(1, 9))
                tmp += symb
            nums.append(tmp)
        return render_template('template.html', nums = nums)

@app.route("/?number=<num>")
def number(num):
    return render_template('number.html', num=num)

if __name__ == "__main__":
    app.run(debug=True)