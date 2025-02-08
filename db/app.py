import json 
from flask import Flask, request, session
from db import db, User, JournalEntry
from datetime import datetime
import os


# define db filename
db_filename = "data.db"
app = Flask(__name__)

# Add secret key for session management
app.secret_key = os.urandom(24)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True


# initialize app
db.init_app(app)
with app.app_context():
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
    try:
        recording_url = body["recording_url"]
    except:
        return failure_response("Invalid request body features; Must contain recording_url, transcription")
    
    user_id = get_current_user()
    new_entry = JournalEntry(user_id=user_id, recording_url=recording_url)
    db.session.add(new_entry)
    db.session.commit()
    return success_response(new_entry.serialize(), 201)



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
    


    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)