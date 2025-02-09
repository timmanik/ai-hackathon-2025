import streamlit as st
import sys
import os
from datetime import datetime

# Add the db directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../db')))
from app import app, JournalEntry

# Configure the page
st.set_page_config(
    page_title="Entries",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,700&display=swap');
    
    .stApp {
        background-color: #f7f1eb;
        color: #2b1810;  /* Updated from #4a3524 */
    }
    .yap-title {
        position: absolute;
        top: 20px;
        font-size: 32px;     /* Made larger */
        font-family: 'Fraunces', serif !important;
        font-weight: bold;
        color: #2b1810;  /* Updated from #4a3524 */
        z-index: 9999;
        background-color: transparent;
        cursor: pointer;  /* Show pointer cursor on hover */
        text-decoration: none;  /* Remove underline */
    }
    .yap-title:hover {
        text-decoration: none;
        color: #2b1810;  /* Updated from #4a3524 */
    }
    .entry-title-header {
        font-size: 2.5rem;
        font-family: 'Fraunces', serif !important;
        font-weight: bold;
        margin-top: 80px;    /* Increased from 60px to 80px */
        margin-bottom: 0.5rem;
        color: #2b1810;  /* Updated from #4a3524 */
    }
    .entry-list {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    .entry-item {
        display: flex;
        justify-content: flex-start;
        padding: 15px 10px;
        border-bottom: 1px solid #2b1810;  /* Updated from #4a3524 */
    }
    .entry-date {
        width: 200px;
        font-weight: normal;
        color: #2b1810;  /* Updated from #4a3524 */
    }
    .entry-title {
        flex-grow: 1;
        text-decoration: none;
        color: #1e88e5;  /* Link color */
    }
    .entry-title:hover {
        text-decoration: underline;
        color: #1565c0;  /* Darker shade on hover */
    }
    </style>
    """, unsafe_allow_html=True)

# Add the yap! title with link
st.markdown('<a href="/" class="yap-title">yap!</a>', unsafe_allow_html=True)

# Function to load entries from database
def load_entries_from_db():
    with app.app_context():
        try:
            # Get all entries, ordered by datetime_created descending (newest first)
            entries = JournalEntry.query.order_by(JournalEntry.datetime_created.desc()).all()
            return entries
        except Exception as e:
            st.error(f"Error loading entries from database: {str(e)}")
            return []

# Add Journal Entries title with new styling
st.markdown('<div class="entry-title-header">Journal Entries</div>', unsafe_allow_html=True)

# Create the entries list
st.markdown('<div class="entry-list">', unsafe_allow_html=True)
entries = load_entries_from_db()
for entry in entries:
    # Format the date and time
    date_str = entry.datetime_created.strftime("%Y-%m-%d")
    time_str = entry.datetime_created.strftime("%H:%M")
    
    st.markdown(f"""
        <div class="entry-item">
            <span class="entry-date">{date_str} {time_str}</span>
            <a href="individualEntry?entry_id={entry.entry_id}" class="entry-title" target="_self">{entry.title}</a>
        </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
