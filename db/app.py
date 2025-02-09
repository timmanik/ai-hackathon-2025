import json 
from flask import Flask, request, session
from db import db, User, JournalEntry
from datetime import datetime
import os


# define db filename
instance_path = os.path.join(os.path.dirname(__file__), "instance")
db_filename = os.path.join(instance_path, "data.db")

app = Flask(__name__)

# Add secret key for session management
app.secret_key = os.urandom(24)

# Use absolute path for database in instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_filename}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True


# initialize app
db.init_app(app)
with app.app_context():
    # Ensure instance directory exists
    os.makedirs(instance_path, exist_ok=True)
    
    db.create_all()
    # Create default user if it doesn't exist
    default_user = User.query.first()
    if not default_user:
        default_user = User()
        db.session.add(default_user)
        db.session.commit()

# Add helper function to get current user
def get_current_user():
    if "user_id" not in session:
        default_user = User.query.first()
        session["user_id"] = default_user.id
    return session["user_id"]

# Add this class for datetime serialization
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Update the success_response function
def success_response(data, code=200):
    return json.dumps(data, cls=DateTimeEncoder), code
def failure_response(message, code=404):
    return json.dumps({"error": message}), code


# user routes
@app.route("/")
def root():
    return success_response({"message": "Journal API active"})

@app.route("/api/journal_entries/", methods=["POST"])
def create_journal_entry():
    body = json.loads(request.data)
    user_id = get_current_user()
    
    print("Received data:", body)  # Add logging
    
    # Extract fields from request body, handling nested dictionaries
    entry_data = {
        "user_id": user_id,
        "title": body.get("title", {}).get("title", "N/A"),  # Extract nested title
        "summary": body.get("summary", {}).get("summary", "N/A"),  # Extract nested summary
        "transcription": body.get("transcription", "N/A"),
        "key_insights": body.get("keypoints", {}).get("key_points", "N/A")  # Extract nested key_points
    }
    
    try:
        print("Creating entry with data:", entry_data)  # Add logging
        new_entry = JournalEntry(**entry_data)
        print("Created JournalEntry object")  # Add logging
        
        db.session.add(new_entry)
        print("Added to session")  # Add logging
        
        db.session.flush()  # Flush to get the ID
        print(f"Entry ID after flush: {new_entry.entry_id}")  # Add logging
        
        db.session.commit()
        print(f"Committed successfully. Entry ID: {new_entry.entry_id}")  # Add logging
        
        # Verify the entry exists
        saved_entry = JournalEntry.query.get(new_entry.entry_id)
        if saved_entry:
            print(f"Successfully verified entry in database: {saved_entry.serialize()}")
        else:
            print("Warning: Entry not found after commit!")
            
        return success_response(new_entry.serialize(), 201)
    except Exception as e:
        print(f"Error creating entry: {str(e)}")  # Add logging
        db.session.rollback()
        return failure_response(f"Failed to create entry: {str(e)}", 500)



@app.route("/api/journal_entries/")
def get_all_journal_entries():
    # Only get entries for current user
    user_id = get_current_user()
    entries = [entry.serialize() for entry in JournalEntry.query.filter_by(user_id=user_id).all()]
    return success_response(entries)

@app.route("/api/journal_entries/<int:entry_id>/", methods=["POST"])
def post_analysis_entry_update(entry_id, **kwargs):
    body = json.loads(request.data)
    try:
        title, summary, transcription, key_insights = body["title"], body["summary"], body["transcription"], body["key_insights"]
    except:
        return failure_response("Invalid request body features; Must contain title, summary, transcription, key_insights")
    
    entry = JournalEntry.query.filter_by(entry_id=entry_id).first()
    if not entry:
        return failure_response("Entry not found")
    
    entry.title = title
    entry.summary = summary
    entry.transcription = transcription
    entry.key_insights = key_insights
    db.session.commit()
    return success_response(entry.serialize())

@app.route("/api/journal_entries/<int:entry_id>/", methods=["DELETE"])
def delete_journal_entry(entry_id):
    """
    Delete a journal entry by its ID
    """
    # Get the entry
    entry = JournalEntry.query.filter_by(entry_id=entry_id).first()
    if not entry:
        return failure_response("Entry not found")
    
    # Verify the entry belongs to the current user
    user_id = get_current_user()
    if entry.user_id != user_id:
        return failure_response("Unauthorized to delete this entry", 403)
    
    # Delete the entry
    db.session.delete(entry)
    db.session.commit()
    
    return success_response({
        "message": f"Entry {entry_id} successfully deleted",
        "deleted_entry": entry.serialize()
    })


@app.route("/api/journal_entries/date/", methods=["Get"])
def get_journal_entries_by_date():
    user_id = get_current_user()
    
    date_str = request.args.get('date')
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return {"error": "Invalid date format, should be YYYY-MM-DD"}, 400
        print("target_date: ", target_date)
        
        start_date = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
        end_date = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)
        
        # Query entries between start and end of the day for the specific user
        entries = JournalEntry.query.filter(
            JournalEntry.user_id == user_id,
            JournalEntry.datetime_created >= start_date,
            JournalEntry.datetime_created <= end_date
        ).all()
        return success_response([entry.serialize() for entry in entries])
    else:
        return {"error": "No date provided"}, 400
    

@app.route("/api/test/")
def test_db():
    try:
        # Try to query the users table
        users = User.query.all()
        return success_response({
            "message": "Database connection successful",
            "user_count": len(users)
        })
    except Exception as e:
        return failure_response(f"Database error: {str(e)}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)