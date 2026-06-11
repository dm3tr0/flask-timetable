from flask import Flask, redirect, render_template, request, jsonify, url_for, g
import sqlite3

app = Flask(__name__)

DATABASE = "timetable.db"

# Creates table when app starts
def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute('''
                CREATE TABLE IF NOT EXISTS timetable (
	            id INTEGER PRIMARY KEY AUTOINCREMENT,
	            transport TEXT NOT NULL,
  	            time TEXT NOT NULL,
  	            city TEXT
                );
                '''
            )
    conn.commit()
    conn.close()

# Connects to database
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

# Closes database connection
@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/")
def main():
    return render_template("base.html")

@app.route("/timetable/<city>")
def timetable(city):
    db = get_db()
    rows = db.execute(f"SELECT * FROM timetable WHERE city='{city}';").fetchall()
    db_items = [dict(row) for row in rows]

    context = {
        'timetable': db_items,
        'city': city,
    }
    return render_template("timetable.html", **context)


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        city = request.form["city"]
        return redirect(url_for("timetable", city=city))
    else:
        return render_template("search.html")

@app.route("/add", methods=["GET", "POST"])
def add_timetable_item():
    if request.method == "POST":
        transport = request.form.get("transport")
        time = request.form.get("time")
        city = request.form.get("city")

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO timetable (transport, time, city) VALUES (?, ?, ?)", (transport, time, city))
        db.commit()

        return redirect(url_for("search"))
    return render_template("add.html")

# API methods

@app.route("/api/timetable", methods=["GET"])
def get_timetables():
    db = get_db()
    rows = db.execute(f"SELECT * FROM timetable").fetchall()
    db_items = [dict(row) for row in rows]

    return jsonify({"timetable":db_items}), 200

@app.route("/api/timetable", methods=["POST"])
def add_timetable():
    data = request.get_json()
    transport = data.get("transport")
    time = data.get("time", "00:00")
    city = data.get("city")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO timetable (transport, time, city) VALUES (?, ?, ?)", (transport, time, city))
    db.commit()

    new_id = cursor.lastrowid
    new_item = {"new_id":new_id, "transport": transport, "time":time, "city":city}
    
    return jsonify({"message": "Item added succesfully", "item":new_item}), 201

@app.route("/api/timetable/<int:item_id>", methods=["PUT"])
def edit_timetable(item_id):
    data = request.get_json()
    db = get_db()

    item = db.execute("SELECT * FROM timetable WHERE id = ?", (item_id,)).fetchone()
    if not item:
        return jsonify({"message": "Error item not found"}), 404
    
    updated_transport = data.get("transport", item["transport"])
    updated_time = data.get("time", item["time"])
    updated_city = data.get("city", item["city"])

    db.execute("UPDATE timetable SET transport = ?, time = ?, city = ? WHERE id = ?", (updated_transport, updated_time, updated_city, item_id))
    db.commit()

    return jsonify({"message": "Item edited succesfully", "item_id":item_id}), 200


@app.route("/api/timetable/<int:item_id>", methods=["DELETE"])
def remove_timetable(item_id):
    db = get_db()
    item = db.execute("SELECT * FROM timetable WHERE id = ?", (item_id,)).fetchone()
    if not item:
        return jsonify({"message": "Error item not found"}), 404
    
    db.execute("DELETE FROM timetable WHERE id = ?", (item_id,))
    db.commit()

    return jsonify({"message": "Item deleted succesfully", "item_id":item_id}), 200


if __name__ == "__main__":
    init_db()
    app.run(debug=True)