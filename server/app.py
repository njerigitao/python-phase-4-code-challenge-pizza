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
def create_restaurant_pizza():
        price=request.form.get("price")
        restaurant_id=request.form.get("restaurant_id")
        pizza_id=request.form.get("pizza_id")

        if not(price and pizza_id and restaurant_id):
            return {'errors': ['All fields are required']}, 400
        
        if not (price.isdigit() and pizza_id.isdigit() and restaurant_id.isdigit()):
            return {'errors': ['Price, pizza_id, and restaurant_id must be integers']}, 400
        
        price = int(price)
        pizza_id = int(pizza_id)
        restaurant_id = int(restaurant_id)

        if price < 1 or price > 30:
            return {'errors': ['Price must be between 1 and 30']}, 400
        
        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if not pizza:
            return {'errors': ['Pizza not found']}, 404
        if not restaurant:
            return {'errors': ['Restaurant not found']}, 404
        
        restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )

        db.session.add(restaurant_pizza)
        db.session.commit()

        restaurant_pizzas = {
            "id": restaurant_pizza.id,
            "pizza": pizza.to_dict(),
            "pizza_id": restaurant_pizza.pizza_id,
            "price": restaurant_pizza.price,
            "restaurant": restaurant.to_dict(),
            "restaurant_id": restaurant_pizza.restaurant_id
        }
        response = make_response(
            restaurant_pizzas,
            201
        )
        return response

if __name__ == "__main__":
    app.run(port=5555, debug=True)
