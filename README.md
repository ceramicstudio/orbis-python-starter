# OrbisDB Python Starter

This repository is a modified version of the Index Network [Ceramic-Python](https://github.com/indexnetwork/ceramic-python) library that includes examples and slight alterations to be compatible with OrbisDB.

## Overview

This demo repository is structured as a simple Flask server that exposes a class called `CeramicActions` found in [examples.py](examples.py). This example architecture emulates an AI agent environment and assigns three imaginary agents individual Ceramic private keys to author data to the network.

Additionally, for no reason in particular, the demo uses a [pageview](definition.json) data model. This has already been deployed to Ceramic, and is therefore provided in the example .env file as the default table value. 

Finally, this demo only uses raw SQL queries to read data. However, OrbisDB also exposes a GraphQL endpoint for read capabilities (that you can easily incorporate into your code if preferred).

## Getting Started

1. Create a copy of the example env file:

```bash
cp .env.example .env
```

2. OrbisDB Setup

To make things simple, we will use the hosted [OrbisDB Studio](https://studio.useorbis.com/) and the shared node instance it provides for this demo, but keep in mind that you can set up your separate instance whenever you want (more details at [OrbisDB](https://useorbis.com/)).

First, sign in with your wallet. 

Once signed in, the studio will default to the `Contexts` tab at the top. On the right-hand side, you will see the shared node endpoints (already provided for you in your env file), as well as your environment ID. Go ahead and assign that value to `ENV_ID` in your new `.env` file.

Next, set up a context. These help developers segment their data models and usage based on the applications they are meant for. Create a new context (call it whatever you like), and assign the resulting string to `CONTEXT_ID` in your `.env` file.

3. Create your virtual environment and install dependencies:

```bash
python3 -m venv myenv
source myenv/bin/activate
pip3 install -r requirements.txt
```

4. Create and assign private Ceramic seeds to each of the agents in your .env file:

```bash
python3 seeds.py
```

Copy the strings corresponding to each agent from your terminal log and assign to each agent.

5. Finally, start your server:

```bash
python3 server.py
```

Your server will now be running on `http://127.0.0.1:5000/`

## Reading and Creating Data

You can reference the pseudocode provided in the [server.py](server.py) file. For example, creating a document:

```bash
curl -X POST "http://127.0.0.1:5000/create_document?agent=agent_three" \
     -H "Content-Type: application/json" \
     -d '{"page": "/home", "address": "0x8071f6F971B438f7c0EA72C950430EE7655faBCe", "customer_user_id": 3}'
```
