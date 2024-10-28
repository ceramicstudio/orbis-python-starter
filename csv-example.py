import os
from dotenv import load_dotenv
from orbis_python import OrbisDB
import json
import csv
from typing import List, Dict


load_dotenv(dotenv_path='.env',override=True)

ENV_ID = os.getenv("ENV_ID")
TABLE_ID = os.getenv("TABLE_ID")
CONTEXT_ID = os.getenv("CONTEXT_ID")
CERAMIC_ENDPOINT = os.getenv("CERAMIC_ENDPOINT")
ORBIS_ENDPOINT = os.getenv("ORBIS_ENDPOINT")

# filename
filename = 'sample.csv'


def create_documents():
    seed = os.urandom(32).hex()
    orbis = OrbisDB(c_endpoint=CERAMIC_ENDPOINT, 
                    o_endpoint=ORBIS_ENDPOINT, 
                    context_stream=CONTEXT_ID, 
                    table_stream=TABLE_ID, 
                    controller_private_key=seed)
    data = []
    with open(filename, mode='r') as file:
        csvFile = csv.DictReader(file)
        for lines in csvFile:
            data.append(lines)
    
    for i in range(len(data)):
        line = data[i]
        # ensure line.customer_user_id is an integer
        line['customer_user_id'] = int(line['customer_user_id'])
        doc = orbis.add_row(line)
        print(doc)
    
    # Return stringified stream_id
    return json.dumps(doc)

create_documents()
