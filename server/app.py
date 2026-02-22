#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

# Create all tables
with app.app_context():
    db.create_all()

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class Restaurants(Resource):
    def get(self):
        return [restaurant.to_dict(rules=('-restaurant_pizzas',)) for restaurant in Restaurant.query.all()], 200


class RestaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter(Restaurant.id == id).one_or_none()
        if restaurant is None:
            return {"error": "Restaurant not found"}, 404
        return restaurant.to_dict(), 200
    
    def delete(self, id):
        restaurant = Restaurant.query.filter(Restaurant.id == id).one_or_none()
        if restaurant is None:
            return {"error": "Restaurant not found"}, 404
        db.session.delete(restaurant)
        db.session.commit()
        return "", 204


class Pizzas(Resource):
    def get(self):
        return [pizza.to_dict(rules=('-restaurant_pizzas',)) for pizza in Pizza.query.all()], 200


class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        try:
            restaurant_pizza = RestaurantPizza(
                price=data.get('price'),
                pizza_id=data.get('pizza_id'),
                restaurant_id=data.get('restaurant_id')
            )
            db.session.add(restaurant_pizza)
            db.session.commit()
            return restaurant_pizza.to_dict(), 201
        except ValueError:
            return {"errors": ["validation errors"]}, 400
        except Exception as e:
            db.session.rollback()
            return {"errors": ["validation errors"]}, 400


api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantById, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')


if __name__ == "__main__":
    app.run(port=5555, debug=True)
