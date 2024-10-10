import os
from dotenv import load_dotenv
from ceramicsdk import OrbisDB
from flask import Flask, request
import json

app = Flask(__name__)

load_dotenv(dotenv_path='.env',override=True)

ENV_ID = os.getenv("ENV_ID")
TABLE_ID = os.getenv("TABLE_ID")
CONTEXT_ID = os.getenv("CONTEXT_ID")
AGENT_ONE_SEED = os.getenv("AGENT_ONE_SEED")
AGENT_TWO_SEED = os.getenv("AGENT_TWO_SEED")
AGENT_THREE_SEED = os.getenv("AGENT_THREE_SEED")
CERAMIC_ENDPOINT = os.getenv("CERAMIC_ENDPOINT")
ORBIS_ENDPOINT = os.getenv("ORBIS_ENDPOINT")

switcher = {
"agent_one": AGENT_ONE_SEED,
"agent_two": AGENT_TWO_SEED,
"agent_three": AGENT_THREE_SEED
}

# GET http://127.0.0.1:5000?agent=agent_two
@app.route('/')
def get():
    agent = request.args.get('agent')
    seed = switcher.get(agent)
    orbis = OrbisDB(c_endpoint=CERAMIC_ENDPOINT, 
                    o_endpoint=ORBIS_ENDPOINT, 
                    context_stream=CONTEXT_ID, 
                    table_stream=TABLE_ID, 
                    controller_private_key=seed)
    return json.dumps(orbis.ceramic_client.did.id)

# POST http://127.0.0.1:5000/create_document?agent=agent_three
# {"page": "/home", "address": "0x8071f6F971B438f7c0EA72C950430EE7655faBCe", "customer_user_id": 3, "timestamp": "2024-09-25T15:06:14.957719+00:00"}
@app.route('/create_document', methods=['POST'])
def create_document():
    agent = request.args.get('agent')
    seed = switcher.get(agent)
    orbis = OrbisDB(c_endpoint=CERAMIC_ENDPOINT, 
                    o_endpoint=ORBIS_ENDPOINT, 
                    context_stream=CONTEXT_ID, 
                    table_stream=TABLE_ID, 
                    controller_private_key=seed)
    content = request.json
    doc = orbis.add_row(content)
    
    # Return stringified stream_id
    return json.dumps(doc)

# GET http://127.0.0.1:5000/get?agent=agent_one
@app.route('/get', methods=['GET'])
def get_documents():
    agent = request.args.get('agent')
    seed = switcher.get(agent)
    orbis = OrbisDB(c_endpoint=CERAMIC_ENDPOINT, 
                    o_endpoint=ORBIS_ENDPOINT, 
                    context_stream=CONTEXT_ID, 
                    table_stream=TABLE_ID, 
                    controller_private_key=seed)
    
    return orbis.read(ENV_ID)

## Need to update below

# # GET http://127.0.0.1:5000/filter?customer_user_id=3&agent=agent_two
# @app.route('/filter')
# def get_filtered_documents():
#     agent = request.args.get('agent')
#     seed = switcher.get(agent)
#     orbis = OrbisDB(c_endpoint=CERAMIC_ENDPOINT, 
#                     o_endpoint=ORBIS_ENDPOINT, 
#                     context_stream=CONTEXT_ID, 
#                     table_stream=TABLE_ID, 
#                     controller_private_key=seed)
    
#     # Get the filter from the query string but remove the agent key
#     filter = {k: v for k, v in request.args.items() if k != 'agent'}
#     res = ceramic.get_with_filter(filter)
#     return res

# # PATCH http://127.0.0.1:5000/update_document?agent=agent_two
# # payload example: {"document_id": "kjzl6kcym7w8y9j9dxto4h933lir60ek5q2r82x3r0ky56fzzty83fovwu4pn6f", "content": {"customer_user_id": 8} }
# @app.route('/update_document', methods=['PATCH'])
# def update_document():
#     agent = request.args.get('agent')
#     ceramic = CeramicActions(agent)
#     ceramic.initialize_ceramic()
#     content = request.json.get('content')
#     document_id = request.json.get('document_id')
#     doc = ceramic.update_document(document_id, content)
#     return json.dumps(doc)

if __name__ == '__main__':
    app.run(debug=True)