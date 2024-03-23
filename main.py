import json
import re
from flask import Flask, request, Response
from extension import db
from tables import Movie, Director
from custom_exceptions import MissedRequiredFieldException, \
                              YearWrongTypeException, \
                              RatingWrongTypeException, \
                              IDWrongTypeException, \
                              FIOWrongTypeException, \
                              TitleWrongTypeException, \
                              MovieLengthTypeException, \
                              DirectorWrongTypeException


app = Flask(__name__)
# create the extension
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://new_user:test@localhost:5432/test"
# initialize the app with the extension
db.init_app(app)


def get_movie_obj_by_id(movie_id):
    movie_obj_from_db = db.session.query(Movie).filter(Movie.id == movie_id).first()
    director_obj_by_id = get_director_obj_by_id(Movie.director)
    return {"id": movie_obj_from_db.id, \
            "title": movie_obj_from_db.title, \
            "year": movie_obj_from_db.year, \
            "director": director_obj_by_id, \
            "length": movie_obj_from_db.length, \
            "rating": movie_obj_from_db.rating}


def get_director_obj_by_id(director_id):
    director_obj_from_db = db.session.query(Director).filter(Director.id == director_id).first()
    return {"id": director_obj_from_db.id, "fio": director_obj_from_db.fio}


def validate_movie_body(input_movie_body):
    # validate JSON schema
    if input_movie_body.get('movie', None) == None:
        # raise custom exc
        raise MissedRequiredFieldException('movie')
    else:
        for req_field in ['id', 'title', 'year', 'director', 'length', 'rating']:
            if input_movie_body['movie'].get(req_field, None) == None:
                # raise custom exc
                raise MissedRequiredFieldException(req_field)
            if type(input_movie_body['movie']['year']) != int or not (1900 <= input_movie_body['movie']['year'] <= 2100):
                # raise custom exc
                raise YearWrongTypeException
            elif type(input_movie_body['movie']['rating']) != int or not (0 <= input_movie_body['movie']['rating'] <= 10):
                # raise custom exc
                raise RatingWrongTypeException
            elif type(input_movie_body['movie']['id']) != int:
                # raise custom exc
                raise IDWrongTypeException
            elif type(input_movie_body['movie']['title']) != str or len(input_movie_body['movie']['title']) > 100:
                # raise custom exc
                raise TitleWrongTypeException
            elif type(input_movie_body['movie']['length']) != str or not re.match(r"[0-9][0-9]:[0-9][0-9]:[0-9][0-9]", input_movie_body['movie']['length']):
                # raise custom exc
                raise MovieLengthTypeException
            validate_director_body(input_movie_body['movie'])
    

def validate_director_body(input_director_body):
    if input_director_body.get('director', None) == None:
        # raise custom exc
        raise MissedRequiredFieldException('director')
    else:
        if type(input_director_body['director']['id']) != int or type(input_director_body['director']['fio']) != str:
            # raise custom exc
            raise DirectorWrongTypeException


@app.errorhandler(MissedRequiredFieldException)
def handle_missed_required(e):
    return Response(json.dumps({"status": 400, "reason": str(e)}, indent=4), status=400, mimetype='application/json')


# error handler
@app.errorhandler(Exception)
def handle_exception(e):
    resp_status = 500
    if isinstance(e, (MissedRequiredFieldException, \
                      YearWrongTypeException, \
                      RatingWrongTypeException, \
                      IDWrongTypeException, \
                      FIOWrongTypeException, \
                      TitleWrongTypeException, \
                      DirectorWrongTypeException, \
                      MovieLengthTypeException)):
        resp_status = 400
    return Response(json.dumps({"status": resp_status, "reason": str(e)}, indent=4), status=resp_status, mimetype='application/json')


@app.route("/api/movies", methods=["GET", "POST"])
def movies_route():
    with app.app_context():
        if request.method == 'GET':
            movies_res = {"list": []}
            movies_list = db.session.query(Movie).all()
            for movie in movies_list:
                movies_res["list"].append(get_movie_obj_by_id(movie.id))
            return Response(json.dumps(movies_res, indent=4), status=200, mimetype='application/json')
        elif request.method == 'POST':
            input_movie_body = request.get_json()
            # validate JSON schema
            validate_movie_body(input_movie_body)
            # check that insertion movie does not exists
            movie_from_db = db.session.query(Movie).filter(Movie.id == input_movie_body['movie']['id']).first()
            if movie_from_db != None:
                return Response(json.dumps({"status": 400, "reason": f"Movie with id={input_movie_body['movie']['id']} already exists"}, indent=4), status=400, mimetype='application/json')
            else:
                if db.session.query(Director).filter(Director.id == input_movie_body['movie']['director']['id']).first() == None:
                    db.session.merge(Director(**input_movie_body['movie']['director']))
                    db.session.commit()
                    print('inserted nwe director')
                db.session.merge(Movie(id=input_movie_body['movie']['id'], \
                                       title=input_movie_body['movie']['title'], \
                                       year=input_movie_body['movie']['year'], \
                                       director=input_movie_body['movie']['director']['id'],\
                                       length=input_movie_body['movie']['length'], \
                                       rating=input_movie_body['movie']['rating']))
                db.session.commit()
                inserted_movie_obj = get_movie_obj_by_id(input_movie_body['movie']['id'])
                return Response(json.dumps(inserted_movie_obj, indent=4), status=200, mimetype='application/json')



@app.route("/api/movie/<id>", methods=["GET", "PATCH", "DELETE"])
def movie_route(id):
    with app.app_context():
        id = int(id)
        if type(id) != int:
            raise IDWrongTypeException
        elif db.session.query(Movie).filter(Movie.id == id).first() == None:
            Response(json.dumps({"status": 404, "reason": f"Movie with id={id} not found"}, indent=4), status=404, mimetype='application/json')
        if request.method == 'GET':
            return get_movie_obj_by_id(id)
        elif request.method == 'PATCH':
            input_movie_body = request.get_json()
            # validate JSON schema
            validate_movie_body(input_movie_body)
            if db.session.query(Director).filter(Director.id == input_movie_body['movie']['director']['id']).first() == None:
                db.session.merge(Director(**input_movie_body['movie']['director']))
            db.session.commit()
            db.session.merge(Movie(id=input_movie_body['movie']['id'], \
                                       title=input_movie_body['movie']['title'], \
                                       year=input_movie_body['movie']['year'], \
                                       director=input_movie_body['movie']['director']['id'],\
                                       length=input_movie_body['movie']['length'], \
                                       rating=input_movie_body['movie']['rating']))
            db.session.commit()
            return get_movie_obj_by_id(id)
        elif request.method == 'DELETE':
            db.session.filter(Movie.id == id).delete()
            db.session.commit()
            return Response(status=202)


@app.route("/api/directors", methods=["GET", "POST"])
def directors_route():
    with app.app_context():
        if request.method == 'GET':
            directors_res = {"list": []}
            directors_list = db.session.query(Director).all()
            for director in directors_list:
                directors_res["list"].append(get_director_obj_by_id(director.id))
            return Response(json.dumps(directors_res, indent=4), status=200, mimetype='application/json')
        elif request.method == 'POST':
            input_director_body = request.get_json()
            # validate JSON schema
            validate_director_body(input_director_body)
            # check that insertion movie does not exists
            director_from_db = db.session.query(Director).filter(Director.id == input_director_body['director']['id']).first()
            if director_from_db != None:
                return Response(json.dumps({"status": 400, "reason": f"Director with id={input_director_body['director']['id']} already exists"}, indent=4), status=400, mimetype='application/json')
            else:
                db.session.merge(Director(**input_director_body['director']))
                db.session.commit()
                inserted_director_obj = get_director_obj_by_id(input_director_body['movie']['id'])
                return Response(json.dumps(inserted_director_obj, indent=4), status=200, mimetype='application/json')


@app.route("/api/director/<id>", methods=["GET", "PATCH", "DELETE"])
def director_route(id):
    with app.app_context():
        id = int(id)
        if type(id) != int:
            raise IDWrongTypeException
        elif db.session.query(Director).filter(Director.id == id).first() == None:
            Response(json.dumps({"status": 404, "reason": f"Director with id={id} not found"}, indent=4), status=404, mimetype='application/json')
        if request.method == 'GET':
            return get_director_obj_by_id(id)
        elif request.method == 'PATCH':
            input_director_body = request.get_json()
            # validate JSON schema
            validate_director_body(input_director_body)
            db.session.merge(Director(**input_director_body['director']))
            db.session.commit()
            return get_director_obj_by_id(id)
        elif request.method == 'DELETE':
            db.session.filter(Director.id == id).delete()
            db.session.commit()
            return Response(status=202)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()