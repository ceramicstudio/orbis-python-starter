import os
from pprint import pprint

def random_seeds():
    string1 = os.urandom(32).hex()
    string2 = os.urandom(32).hex()
    string3 = os.urandom(32).hex()
    
    obj = {
        "agent_one": string1,
        "agent_two": string2,
        "agent_three": string3
    }
        
    pprint(obj)
    return obj

random_seeds()