from pymongo import MongoClient
from pymongo.server_api import ServerApi

# MongoDB Connection URI
uri = "mongodb+srv://root:root@techstax.3pucb.mongodb.net/?retryWrites=true&w=majority&appName=TechStax"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("You successfully connected to MongoDB!")
except Exception as e:
    print("MongoDb connection error: ",e)

# Access the database and collection
db = client["Webhook_db"]
collection = db["github_events"]