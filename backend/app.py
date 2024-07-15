from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

client = MongoClient("mongodb://localhost:27017/")
db = client["dishesDB"]
collection = db["dishes"]

@app.route('/api/dishes', methods=['GET'])
def get_dishes():
    dishes = list(collection.find({}, {"_id": 0}))
    return jsonify(dishes)

@app.route('/api/dishes/toggle/<int:dish_id>', methods=['POST'])
def toggle_dish(dish_id):
    dish = collection.find_one({"dishId": str(dish_id)})
    if dish:
        new_status = not dish["isPublished"]
        collection.update_one({"dishId": str(dish_id)}, {"$set": {"isPublished": new_status}})
        updated_dish = collection.find_one({"dishId": str(dish_id)}, {"_id": 0})
        socketio.emit('dish_status_changed', updated_dish)
        return jsonify({"success": True, "isPublished": new_status})
    else:
        return jsonify({"success": False, "message": "Dish not found"}), 404

if __name__ == '__main__':
    socketio.run(app, debug=True)
