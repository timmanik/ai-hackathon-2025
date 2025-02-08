from flask_sqlalchemy import SQLAlchemy
from datetime import datetime




db = SQLAlchemy()

class User(db.Model):
    """
    User model - simplified for MVP with single user
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, nullable=False)
    
    journal_entries = db.relationship("JournalEntry", back_populates="user")

    def __init__(self, **kwargs):
        self.created_at = datetime.now()

    def serialize(self):
        return {
            "id": self.id,
            "created_at": self.created_at
        }
        
class JournalEntry(db.Model):
    """
    Journal Entry model
    Has a one-to-many relationship with users
    """
    __tablename__ = "journal_entries"
    __table_args__ = {'sqlite_autoincrement': True}  # This ensures SQLite never reuses IDs
    
    # Modified entry_id to ensure globally unique IDs
    entry_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recording_url = db.Column(db.String, nullable=True, default="N/A")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    datetime_created = db.Column(db.DateTime, nullable=False)
    
    # Add after analysis
    title = db.Column(db.String, nullable=True, default="N/A")
    summary = db.Column(db.String, nullable=True, default="N/A")
    transcription = db.Column(db.String, nullable=True, default="N/A")
    key_insights = db.Column(db.String, nullable=True, default="N/A")
    #one_word_sentiment = db.Column(db.String, nullable=True, default="N/A")
    
    
    # Add relationship to user
    user = db.relationship("User", back_populates="journal_entries")
    
    def __init__(self, **kwargs):
        self.user_id = kwargs.get("user_id")
        self.recording_url = kwargs.get("recording_url")
        #self.transcription = kwargs.get("transcription")
        self.datetime_created = kwargs.get("datetime_created") or datetime.now()

    def serialize(self):
        return {
            "entry_id": self.entry_id,
            "user_id": self.user_id,
            "title": self.title,
            "datetime_created": self.datetime_created,
            "recording_url": self.recording_url,
            "transcription": self.transcription,
            "summary": self.summary,
            "key_insights": self.key_insights,
            #"one_word_sentiment": self.one_word_sentiment
        }
    
    
    
    

    
            
        