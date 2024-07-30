from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError

app = Flask(__name__)

# MongoDB Atlas connection URI and database configuration
uri = 'mongodb+srv://swayam88:1234@cluster0.wnwpthu.mongodb.net/product?retryWrites=true&w=majority'
db_name = 'product'
collection_name = 'product'

# Connect to MongoDB Atlas
try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)  # Timeout after 5 seconds
    db = client[db_name]
    print('Connected to MongoDB Atlas')
except ConnectionFailure as e:
    print(f'Error connecting to MongoDB Atlas: {e}')

@app.route('/checkUID', methods=['GET'])
def check_uid():
    uid = request.args.get('uid')
    if not uid:
        return jsonify({'error': 'UID is required'}), 400
    try:
        collection = db[collection_name]
        product = collection.find_one({'UID': uid})
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        return jsonify({'success': True, 'product': product})
    except PyMongoError as e:
        print(f'Error processing request: {e}')
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/purchaseProduct', methods=['POST'])
def purchase_product():
    uid = request.json.get('uid')
    if not uid:
        return jsonify({'error': 'UID is required'}), 400
    try:
        collection = db[collection_name]
        product = collection.find_one({'UID': uid})
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        if product['ProductOwner'] == 'supermarket':
            result = collection.update_one({'UID': uid}, {'$set': {'ProductOwner': 'swayam_raut'}})
            if result.modified_count > 0:
                return jsonify({'success': True, 'message': 'Product purchased successfully', 'product': product})
            else:
                return jsonify({'error': 'Product update failed'}), 400
        else:
            return jsonify({'success': True, 'message': 'Product already owned', 'product': product})
    except PyMongoError as e:
        print(f'Error processing request: {e}')
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/returnProduct', methods=['POST'])
def return_product():
    uid = request.json.get('uid')
    if not uid:
        return jsonify({'error': 'UID is required'}), 400
    try:
        collection = db[collection_name]
        result = collection.update_one({'UID': uid, 'ProductOwner': 'swayam_raut'}, {'$set': {'ProductOwner': 'supermarket'}})
        if result.modified_count > 0:
            return jsonify({'success': True, 'message': 'Product returned to supermarket'})
        else:
            return jsonify({'error': 'Product not found or not owned by swayam_raut'}), 404
    except PyMongoError as e:
        print(f'Error processing request: {e}')
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/purchases', methods=['GET'])
def purchases():
    try:
        collection = db[collection_name]
        products = list(collection.find({'ProductOwner': 'swayam_raut'}))
        return jsonify(products)
    except PyMongoError as e:
        print(f'Error processing request: {e}')
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    port = 3001
    app.run(host='0.0.0.0', port=port)
