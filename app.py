import os
from flask import jsonify, request,Flask
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

MONGO_HOST = os.environ.get("MONGO_HOST", "localhost")
MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))
MONGO_DB = os.environ.get("MONGO_DB", "corider")

# app.config['MONGO_URI'] = "mongodb://localhost:27017/CoRider"

# mongo = PyMongo(app)
client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
db = client[MONGO_DB]

user_fields = ['name','email','password']

def id_toString(user):
    user['_id'] = str(user['_id'])
    return user

@app.route('/users', methods=['POST'])
def create_user():
    _json = request.json
    for field in user_fields:
        if field not in _json:
            return jsonify({'message': f'Missing {field} field'}), 400
    user_id = db.users.insert_one({'name':_json['name'],'email':_json['email'],'password':_json['password']}).inserted_id
    new_user = db.users.find_one({'_id': user_id})
    new_user = id_toString(new_user)
    return jsonify(new_user), 201

@app.route('/users/<string:user_id>', methods=['PUT'])
def update_user(user_id):
    _json = request.json
    updated_user = db.users.find_one_and_update(
        {'_id': ObjectId(user_id)},
        {'$set': _json},
        return_document=True
    )
    if updated_user:
        updated_user = id_toString(updated_user)
        return jsonify(updated_user)
    else:
        return jsonify({'message': 'User not found'}), 404

@app.route('/users', methods=['GET'])
def get_users():
    users = list(db.users.find())
    users = [id_toString(user) for user in users]
    return jsonify(users)

@app.route('/users/<string:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.users.find_one({'_id': ObjectId(user_id)})
    if user:
        user = id_toString(user)
        return jsonify(user)
    else:
        return jsonify({'message': 'User not found'}), 404
    
@app.route('/users/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    result = db.users.delete_one({'_id': ObjectId(user_id)})
    if result.deleted_count > 0:
        return jsonify({'message': 'User deleted successfully'})
    else:
        return jsonify({'message': 'User not found'}), 404

if __name__=="__main__":
    app.run(debug=True)