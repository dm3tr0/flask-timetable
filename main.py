from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("base.html")

def timetable():
    return render_template("timetable.html")
app.add_url_rule("/timetable", "timetable_path", timetable)


@app.route("/user/<name>")
def user_profile(name):
    return "Hello, {}".format(name)


if __name__ == "__main__":
    app.run(debug=True)