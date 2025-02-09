from app import app, JournalEntry

def view_all_entries():
    with app.app_context():
        entries = JournalEntry.query.all()
        print(f"\nTotal entries: {len(entries)}\n")
        
        for entry in entries:
            print(f"Entry ID: {entry.entry_id}")
            print(f"Title: {entry.title}")
            print(f"Created: {entry.datetime_created}")
            print(f"Transcription: {entry.transcription}")
            print(f"Summary: {entry.summary}")
            print(f"Key Insights: {entry.key_insights}")
            print("-" * 80 + "\n")

if __name__ == "__main__":
    view_all_entries() 