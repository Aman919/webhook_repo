from flask import Blueprint, request, jsonify
from db import collection
from datetime import datetime
from enum import Enum
from bson import ObjectId

class EventType(Enum):
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    MERGE = "merge"

# Helper function to get current UTC timestamp in formatted string
def get_utc_timestamp():
    return datetime.utcnow().strftime("%d %b %Y - %I:%M %p UTC")

    
# Function to serialize ObjectId
def serialize_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError("Type not serializable")

webhook_blueprint = Blueprint("webhook", __name__)

@webhook_blueprint.route("/webhook", methods=["POST"])
def webhook():
    event_data = {}
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({"error": "No Json payload received"}), 400

        # push request
        if "commits" in payload:
            messages = []
            for commit in payload.get("commits", []):
                author = commit.get("author", {}).get("name", "Unknown")
                to_branch = payload.get("ref", "").split("/")[-1]
                timestamp = commit.get("timestamp", "Unknown")
                messages.append(f'{author} pushed to {to_branch} on {timestamp}')
                
                event_data = {
                    "request_id": commit.get("id"),
                    "author": author,
                    "action": EventType.PUSH.value,
                    "from_branch": "",  # Missing value for from_branch
                    "to_branch": to_branch,
                    "timestamp": get_utc_timestamp()
                }
            # Log response content
            response = jsonify({"message": messages})
            print("Webhook response: ", response.get_json())
            # return response

        # pull request
        elif "pull_request" in payload:
            action = payload.get("action")
            pull_request = payload["pull_request"]
            from_branch = pull_request["head"]["ref"]
            to_branch = pull_request["base"]["ref"]
            author = pull_request["user"]["login"]
            message = f"{author} {action} a pull request from {from_branch} to {to_branch}"

            event_data = {
                "request_id": payload.get("pull_request", {}).get("number"),
                "author": author,
                "action": EventType.PULL_REQUEST.value,
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": get_utc_timestamp()
            }

            response = jsonify({"message": message})
            print("Webhook response: ", response.get_json())
            # return response

        # merge request
        else:
            return jsonify({"error": "Invalid Content-Type"}), 400
        
        # Insert the event data into db
        result = collection.insert_one(event_data)
        event_data["_id"] = str(result.inserted_id)
        return jsonify({"message": "Event received and stored", "event": event_data}), 200

    except Exception as e:
        print("Error: ", str(e))
        return jsonify({"error": f"Error processing the webhook: {str(e)}"}), 400


@webhook_blueprint.route("/events", methods=["GET"])
def show_events():
    # Fetch all events from the database sorted by timestamp (most recent first)
    events = collection.find().sort("timestamp", -1)

    # Format the events
    formatted_events = []
    for event in events:
        event["_id"] = str(event["_id"])  # Convert ObjectId to string
        timestamp = event.get("timestamp", "Unknown")

        if "action" in event and event["action"] == EventType.PUSH.value:
            formatted_event = f'{event["author"]} pushed to "{event["to_branch"]}" on {timestamp}'
        elif "action" in event and event["action"] == EventType.PULL_REQUEST.value:
            formatted_event = f'{event["author"]} submitted a pull request from "{event["from_branch"]}" to "{event["to_branch"]}" on {timestamp}'
      
        formatted_events.append(formatted_event)

    return jsonify({"events": formatted_events})
