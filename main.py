from flask import Flask, redirect, render_template, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy # type: ignore


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/timetable' # change to your settings

db = SQLAlchemy(app)

# Models (Tables)

class City(db.Model):
    __tablename__ = "cities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    timetable_items = db.relationship('Timetable', backref='city', cascade='all, delete-orphan', lazy=True)

    def to_json(self):
        return {'id':self.id, 'name':self.name}


class Timetable(db.Model):
    __tablename__ = "timetable"

    id = db.Column(db.Integer, primary_key=True)
    vehicle = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False, default="00:00")

    city_id = db.Column(db.Integer, db.ForeignKey("cities.id"), nullable=False)


# Creates table when app starts
def init_db():
    with app.app_context():
        db.create_all()

        if City.query.count() == 0:
            kyiv = City(name="Kyiv")
            kharkiv = City(name="Kharkiv")
            ivano_frankivsk = City(name="Ivano-Frankivsk")

            db.session.add_all([kyiv, kharkiv, ivano_frankivsk])
            db.session.commit()
            print("Added three base cities!")


@app.route("/")
def main():
    return render_template("base.html")


@app.route("/timetable/<city>")
def timetable(city):
    city_obj = City.query.filter(City.name.ilike(city)).first()

    if not city_obj or not city_obj.timetable_items:
        return f"No timetables for {city}"

    context = {
        'timetable': city_obj.timetable_items,
        'city': city_obj.name,
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
        city_obj = City.query.filter(City.name.ilike(city)).first()

        if not city_obj:
            return f"No cities with name {city}"

        new_item = Timetable(
            vehicle=transport,
            time=time,
            city_id=city_obj.id,
        )
        db.session.add(new_item)
        db.session.commit()

        return redirect(url_for("search"))
    return render_template("add.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)