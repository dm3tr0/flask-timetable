from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("base.html")

@app.route("/timetable")
def timetable():
    city = "Odessa"
    timetable = [
        ["Bus 2", "18:00"],
        ["Train 17", "15:00"],
        ["Tram 33", "14:30"],
        ["Plane 111", "2:30"],
    ]
    context = {
        'timetable': timetable,
        'city': city,
        'role': "User",
    }
    return render_template("timetable.html", **context)


@app.route("/user/<name>")
def user_profile(name):
    return "Hello, {}".format(name)


if __name__ == "__main__":
    app.run(debug=True)