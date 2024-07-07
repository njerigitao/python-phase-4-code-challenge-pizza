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
        response = make_response
    

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    
    restaurant_pizzas = RestaurantPizza.query.filter_by(restaurant_id=id).all()
    for restaurantpizza in restaurant_pizzas:
        db.session.delete(restaurantpizza)
    
    db.session.delete(restaurant)
    db.session.commit()

    return '', 204

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizza_list = []
    for pizza in pizzas:
        pizza_data = {
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients       
        }
        pizza_list.append(pizza_data)
    return jsonify(pizza_list)

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()

    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    if not (price and pizza_id and restaurant_id):
        return jsonify({"errors": ["validation errors"]}), 400
    
    pizza = db.session.get(Pizza, pizza_id)
    restaurant = db.session.get(Restaurant, restaurant_id)

    if not pizza:
        return jsonify({"errors": ["Pizza not found"]}), 404
    
    if not restaurant:
        return jsonify({"errors": ["Restaurant not found"]}), 404
    
    try:
        validated_price = int(price)
        if not (1 <= validated_price <= 30):
            return jsonify({"errors": ["validation errors"]}), 400
    except ValueError:
        return jsonify({"errors": ["validation errors"]}), 400
    
    new_restaurant_pizza = RestaurantPizza(
        price=validated_price,
        pizza_id=pizza_id,
        restaurant_id=restaurant_id
    )

    try:
        db.session.add(new_restaurant_pizza)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 500
    
    response_data = {
        "id": new_restaurant_pizza.id,
        "pizza": {
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients
        },
        "pizza_id": new_restaurant_pizza.pizza_id,
        "price": new_restaurant_pizza.price,
        "restaurant": {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address
        },
        "restaurant_id": new_restaurant_pizza.restaurant_id
    }

    return jsonify(response_data), 201

if __name__ == "__main__":
    app.run(port=5555, debug=True)
