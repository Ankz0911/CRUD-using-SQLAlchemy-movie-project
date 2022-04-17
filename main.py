from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from Functions import get_list, get_movie_details

# app initialisation
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Movie.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)


# Database Fields
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(250), unique=False, nullable=True)
    year = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(250), nullable=True)
    rating = db.Column(db.Float, unique=False, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=True)

    def __repr__(self):
        return f'<Book {self.title}>'


# Form Creation
class Edit_form(FlaskForm):
    rating = StringField('Your Ratings out of 10', validators=[DataRequired()])
    review = StringField('Your Review', validators=[DataRequired()])
    submit = SubmitField('done')


class Add_form(FlaskForm):
    movie_name = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')


# route creations
@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", all_movies=all_movies)


@app.route("/edit", methods=["POST", "GET"])
def edit_details():
    if request.method == "GET":
        movie_id = request.args.get("movie_id")
        movie_selected = Movie.query.get(movie_id)
        my_form = Edit_form()
        return render_template("edit.html", movie_selected=movie_selected, form=my_form)
    else:
        new_rating = request.form["rating"]
        new_review = request.form["review"]
        movie_id = request.args.get("movie_id")
        movie_to_update = Movie.query.filter_by(id=movie_id).first()
        movie_to_update.rating = new_rating
        movie_to_update.review = new_review
        db.session.commit()
        return redirect(url_for('home'))


@app.route("/delete", methods=["POST", "GET"])
def delete_movie():
    movie_id = request.args.get("movie_id")
    movie_selected = Movie.query.get(movie_id)
    db.session.delete(movie_selected)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["POST", "GET"])
def add_movie():
    form = Add_form()
    if form.validate_on_submit():
        movie_name = request.form["movie_name"]
        movies_list = get_list(movie_name)
        return render_template("select.html", movies_list=movies_list)
    else:
        return render_template("add.html", form=form)


@app.route("/select", methods=["POST", "GET"])
def select_movie():
    movie_id_moviedb = request.args.get("movie_id")
    movie_details = get_movie_details(movie_id_moviedb)
    movie_to_be_added = Movie(title=movie_details["title"], img_url=movie_details["img_url"],
                              year=movie_details["year"],
                              description=movie_details["description"])
    db.session.add(movie_to_be_added)
    db.session.commit()
    return redirect(url_for('edit_details', movie_id=movie_to_be_added.id))


if __name__ == '__main__':
    app.run(debug=True)
