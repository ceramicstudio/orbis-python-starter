from http.server import HTTPServer, BaseHTTPRequestHandler
from examples import CeramicActions
from flask import Flask, request
import json

app = Flask(__name__)

# GET http://127.0.0.1:5000?agent=agent_two
@app.route('/')
def get():
    agent = request.args.get('agent')
    ceramic = CeramicActions(agent)
    ceramic.initialize_ceramic()
    # Return stringified did
    return json.dumps(ceramic.did)

# POST http://127.0.0.1:5000/create_document?agent=agent_three
# payload example: {"page": "/home", "address": "0x8071f6F971B438f7c0EA72C950430EE7655faBCe", "customer_user_id": 3}
@app.route('/create_document', methods=['POST'])
def create_document():
    agent = request.args.get('agent')
    ceramic = CeramicActions(agent)
    ceramic.initialize_ceramic()
    content = request.json
    doc = ceramic.create_document(content)
    
    # Return stringified stream_id
    return json.dumps(doc.stream_id)

# GET http://127.0.0.1:5000?agent=agent_one
@app.route('/get')
def get_documents():
    agent = request.args.get('agent')
    ceramic = CeramicActions(agent)
    return ceramic.get_all_documents()

# GET http://127.0.0.1:5000/filter?customer_user_id=3&agent=agent_two
@app.route('/filter')
def get_filtered_documents():
    agent = request.args.get('agent')
    ceramic = CeramicActions(agent)
    
    # Get the filter from the query string but remove the agent key
    filter = {k: v for k, v in request.args.items() if k != 'agent'}
    res = ceramic.get_with_filter(filter)
    return res

# PATCH http://127.0.0.1:5000/update_document?agent=agent_two
# payload example: {"document_id": "kjzl6kcym7w8y9j9dxto4h933lir60ek5q2r82x3r0ky56fzzty83fovwu4pn6f", "content": {"customer_user_id": 8} }
@app.route('/update_document', methods=['PATCH'])
def update_document():
    agent = request.args.get('agent')
    ceramic = CeramicActions(agent)
    ceramic.initialize_ceramic()
    content = request.json.get('content')
    document_id = request.json.get('document_id')
    doc = ceramic.update_document(document_id, content)
    return json.dumps(doc)

if __name__ == '__main__':
    app.run(debug=True)