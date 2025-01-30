from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import toml


with open('config.toml', 'r') as f:
    config = toml.load(f)

uri = config['database']['MONGODB_URL']

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.Blogging 
db2 = client.sample_mflix
blogs_collection = db["blogs"]
user_collection = db2["users"]

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("You successfully connected to MongoDB!")
except Exception as e:
    print(e)