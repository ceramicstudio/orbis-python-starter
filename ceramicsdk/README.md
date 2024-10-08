# Ceramic and OrbisDB Python Client

These Orbis and Ceramic clients implements the payload building, encoding, and signing needed to interact with the [Ceramic Network](https://ceramic.network/). It currently supports `ModelInstanceDocument`.

## Features

- Implements payload building, encoding, and signing for Ceramic interactions
- Currently supports `ModelInstanceDocument`

## Install the library using pip

```bash
pip3 install ceramicsdk
```

### Instantiating a Client

You can use the [Orbis Studio](https://studio.useorbis.com/) or run a local or self-hosted [OrbisDB Instance](https://orbisclub.notion.site/Local-d3e9dd97e97b4c00a530b6ada20a8536) to locate and configure your context ID, environment ID, and node endpoints (used below).

This README will utilize this [data model](https://cerscan.com/mainnet/stream/kjzl6hvfrbw6c6adsnzvbyr6itmf0igfy25xu0mqzei2pe2xw1hlusqyuknb9ky) as the input example.

First, generate a Decentralized Identifier (DID) using a DID library.

```python
from ceramicsdk import OrbisDB

# using an existing data model example
table = "kjzl6hvfrbw6c6adsnzvbyr6itmf0igfy25xu0mqzei2pe2xw1hlusqyuknb9ky"

# using an existing context id
context = "<your-context-here>"

# dedicated orbis and ceramic endpoints 
o_endpoint = "<your-endpoint-here>"
c_endpoint = "<your-endpoint-here>"

# create a private key
privkey = os.urandom(32).hex()

# creating a client
db = OrbisDB(c_endpoint, o_endpoint, context, table, privkey)
```

### Creating a Row

```python
# input content must conform to data model used
doc = db.add_row({
    page: "/home",
    address: "0x8071f6F971B438f7c0EA72C950430EE7655faBCe",
    customer_user_id: 3,
    timestamp: "2024-09-25T15:06:14.957719+00:00"
})
```

### Reading Data

```python
env_id = "<your-env-id-here>"

# select rows without any filters
docs = orbis.read(env_id)

# using a defined query
q = 'SELECT * FROM kjzl6hvfrbw6c6adsnzvbyr6itmf0igfy25xu0mqzei2pe2xw1hlusqyuknb9ky as table WHERE table.customer_user_id = 3'
queried_rows = db.query(env_id, q)
```

### Updating Data

```python
# add a filter to select specific row
filters={"customer_user_id": 3}

# new content to replace the old
new_content={"customer_user_id": 2}

updated_rows = db.update_rows(env_id, filters, new_content)
```


## Credits

This project is largely based on the work done by the team at https://github.com/valory-xyz/ceramic-py/, and by the team at https://github.com/indexnetwork/ceramic-python. We are grateful for their contributions to the Ceramic ecosystem and the open-source community.