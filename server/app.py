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

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = [restaurant.to_dict() for restaurant in Restaurant.query.all()]
    response = make_response(
        restaurants,
        200
    )
    return response

@app.route('/restaurants/<int:id>', methods=['GET'])
def restaurant_by_id(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()

    if restaurant:
        response = make_response(
            restaurant.to_dict(),
            200
        )
    else:
        response = make_response(
            {"error": "Restaurant not found"},
            404
        )
    return response

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        response = make_response(
            '', 
            204
        )
    else:
        response = make_response({"error": "Restaurant not found"}, 404)
    return response

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = [pizza.to_dict() for pizza in Pizza.query.all()]
    response = make_response(
        pizzas, 
        200
    )

    return response

@app.route('/restaurant_pizzas', methods=['POST'])
def restaurant_pizzas():
    new_restaurant_pizza = RestaurantPizza(
        price=request.form.get("price"),
        restaurant_id=request.form.get("restaurant_id"),
        pizza_id=request.form.get("pizza_id"),
    )

    if new_restaurant_pizza:

       db.session.add(new_restaurant_pizza)
       db.session.commit()
       response = make_response(new_restaurant_pizza.to_dict(), 201)
    else:
        response = make_response({"errors": "validation errors" }, 400)
    
    return response

if __name__ == "__main__":
    app.run(port=5555, debug=True)
