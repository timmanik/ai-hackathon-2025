import streamlit as st
import json
from pathlib import Path

# Configure the page
st.set_page_config(
    page_title="Entries",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFDD0;  /* Light cream color - same as Home.py */
        color: black;
    }
    .yap-title {
        position: absolute;
        top: 20px;
        font-size: 32px;     /* Made larger */
        font-weight: bold;
        color: #000000;
        z-index: 9999;
        background-color: transparent;
        pointer-events: none;
    }
    .entry-title-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-top: 60px;    /* Added margin-top to create space */
        margin-bottom: 0.5rem;
        color: #000000;
        padding: 20px 0 20px 20px;
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
        border-bottom: 1px solid #ddd;
    }
    .entry-date {
        width: 200px;
        font-weight: normal;
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

# Add the yap! title
st.markdown('<div class="yap-title">yap!</div>', unsafe_allow_html=True)

# Load sample entries from JSON file
def load_entries():
    json_path = Path(__file__).parent / "sample_entries.json"
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Sample entries file not found")
        return []

# Add Journal Entries title with new styling
st.markdown('<div class="entry-title-header">Journal Entries</div>', unsafe_allow_html=True)

# Create the entries list
st.markdown('<div class="entry-list">', unsafe_allow_html=True)
entries = load_entries()
for i, entry in enumerate(entries):
    st.markdown(f"""
        <div class="entry-item">
            <span class="entry-date">{entry['date']} {entry['time']}</span>
            <a href="individualEntry?entry_id={i}" class="entry-title" target="_self">{entry['title']}</a>
        </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
