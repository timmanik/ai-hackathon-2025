from app import app, db, User, JournalEntry

def check_database():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check if default user exists
        default_user = User.query.first()
        if not default_user:
            print("Creating default user...")
            default_user = User()
            db.session.add(default_user)
            db.session.commit()
        
        # Print current users
        print("\nCurrent Users:")
        users = User.query.all()
        for user in users:
            print(f"User ID: {user.id}, Created at: {user.created_at}")
        
        # Print current journal entries
        print("\nCurrent Journal Entries:")
        entries = JournalEntry.query.all()
        for entry in entries:
            print(f"Entry ID: {entry.entry_id}")
            print(f"Title: {entry.title}")
            print(f"Created at: {entry.datetime_created}")
            print("---")

if __name__ == "__main__":
    check_database() 