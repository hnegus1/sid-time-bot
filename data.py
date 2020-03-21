from pymongo import MongoClient
from datetime import datetime


from dotenv import load_dotenv

load_dotenv()

USER = os.getenv('CONNECTION_USER')
PASS = os.getenv('CONNECTION_PASS')

client = MongoClient(f'mongodb+srv://{USER}:{PASS}@harry-n-rbsaq.azure.mongodb.net/test?retryWrites=true&w=majority')
db = client['sid-time-bot']
events = db.events
names = db.users

def add_event(name, minutes, channel_id):
    events.insert_one({
        "minutes": minutes,
        "time": datetime.now(),
        "user": {
            "name": name,
            "user_id": find_user_id(name) 
        },
        "actual_time": None,
        "channel_id": channel_id

    })

def find_incomplete_event(user_id):
    return events.find_one({"$and": [{"user.user_id": str(user_id)}, {"actual_time": None}]})

def complete_event(user_id):
    events.update_one({"user.user_id": str(user_id), "actual_time": None}, {"$set": {"actual_time": datetime.now()}})
    
def validate_name(name):
    my_names = list(names.find())
    for my_name in my_names:
        if name.lower() in my_name.get('names'):
            return True
    return False

def find_user_id(name):
    my_names = list(names.find())
    for my_name in my_names:
        if name.lower() in my_name.get('names'):
            return my_name.get('user_id')