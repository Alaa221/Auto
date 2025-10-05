from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cars.db"
app.config["UPLOAD_FOLDER"] = "static/uploads"
db = SQLAlchemy(app)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    condition = db.Column(db.String(100))
    color = db.Column(db.String(50))
    description = db.Column(db.Text)
    image = db.Column(db.String(200))
    reserved = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        condition = request.form["condition"]
        color = request.form["color"]
        description = request.form["description"]

        image_file = request.files["image"]
        image_path = ""
        if image_file and image_file.filename:
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_file.filename)
            image_file.save(image_path)
            image_path = "/" + image_path  # لعرض الصورة لاحقًا

        new_car = Car(
            name=name,
            condition=condition,
            color=color,
            description=description,
            image=image_path
        )
        db.session.add(new_car)
        db.session.commit()
        return redirect(url_for("index"))

    search_query = request.args.get("search", "")
    if search_query:
        cars = Car.query.filter(Car.name.contains(search_query)).all()
    else:
        cars = Car.query.all()
    return render_template("index.html", cars=cars, search_query=search_query)

@app.route("/reserve/<int:car_id>")
def reserve(car_id):
    car = Car.query.get_or_404(car_id)
    car.reserved = not car.reserved
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete/<int:car_id>")
def delete(car_id):
    car = Car.query.get_or_404(car_id)
    db.session.delete(car)
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
