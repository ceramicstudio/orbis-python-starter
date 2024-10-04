from clients.orbis_python.orbis_db import OrbisDB
import os

CONTEXT_ID = os.getenv("CONTEXT_ID")

# Setup a table stream and a private key for the DID
table_stream = "kjzl6hvfrbw6c6adsnzvbyr6itmf0igfy25xu0mqzei2pe2xw1hlusqyuknb9ky"
did_pkey = os.urandom(32).hex()

# Instantiate a read-only db
db = OrbisDB.from_stream(table_stream)

# Read the whole db
print(db.read())

# Instantiate a read and write db
db = OrbisDB(context_stream=CONTEXT_ID, table_stream=table_stream, controller_private_key=did_pkey)

# Add a new row
db.add_row({"user_id": 2, "user_name": "test_user_3", "user_points": 1000})

# Select some rows
print(db.filter({"user_points": 1000}))

# Update a row batch
db.update_rows(filters={"user_name": "test_user_3"}, new_content={"user_points": 2000})

# Dump the db to a local json file
db.dump()