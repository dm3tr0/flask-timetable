from flask import Flask, redirect, render_template, request, jsonify, url_for

app = Flask(__name__)

# тимчасова база даних
db = [
    {"id": 1, "transport": "Bus", "time": "15:00"},
    {"id": 2, "transport": "Train", "time": "13:30"}
]


@app.route("/")
def main():
    return render_template("base.html")

@app.route("/timetable/<city>")
def timetable(city):
    context = {
        'timetable': db,
        'city': city,
        'role': "User",
    }
    return render_template("timetable.html", **context)


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        city = request.form["city"]
        return redirect(url_for("timetable", city=city))
    else:
        return render_template("search.html")

@app.route("/user/<name>")
def user_profile(name):
    return "Hello, {}".format(name)


@app.route("/api/timetable", methods=["GET"])
def get_timetables():
    return jsonify({"timetable":db}), 200


@app.route("/api/timetable", methods=["POST"])
def add_timetable():
    data = request.get_json()
    new_item = {"id": max([i["id"] for i in db])+1, 
                "transport": data.get("transport"),
                "time": data.get("time", "00:00")
                }
    db.append(new_item)
    return jsonify({"message": "Item added succesfully", "item":new_item}), 201


@app.route("/api/timetable/<int:item_id>", methods=["PUT"])
def edit_timetable(item_id):
    data = request.get_json()

    for item in db:
        if item["id"] == item_id:
            item["transport"] = data.get("transport", item["transport"])
            item["time"] = data.get("time", item["time"])
            return jsonify({"message": "Item edited succesfully", "item":item}), 200

    return jsonify({"message": "Error item not found"}), 404


@app.route("/api/timetable/<int:item_id>", methods=["DELETE"])
def remove_timetable(item_id):
    global db

    for item in db:
        if item["id"] == item_id:
            db = [i for i in db if i["id"] != item_id]
            return jsonify({"message": "Item deleted succesfully", "item_id":item_id}), 200

    return jsonify({"message": "Error item not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)