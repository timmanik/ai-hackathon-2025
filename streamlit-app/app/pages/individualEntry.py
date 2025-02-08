import streamlit as st
from pathlib import Path
import json
from urllib.parse import parse_qs

def load_entry(entry_id):
    """Load and return a specific entry by ID"""
    json_path = Path(__file__).parent / "sample_entries.json"
    try:
        with open(json_path, 'r') as f:
            entries = json.load(f)
            return entries[entry_id] if 0 <= entry_id < len(entries) else None
    except (FileNotFoundError, ValueError, IndexError):
        return None

def display_entry(entry):
    """Display a single entry with its full content"""
    st.markdown("""
    <style>
    .stApp {
        background-color: #FFFDD0;
        color: #000000;
    }
    /* Override Streamlit's default text colors */
    .stMarkdown, .stText, p, span, div {
        color: #000000 !important;
    }
    .entry-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #000000;
    }
    .entry-date {
        font-style: italic;
        color: #666;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #000000;
    }
    .content-box {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #000000;
    }
    .bullet-point {
        margin-bottom: 0.5rem;
        color: #000000;
    }
    /* Style for the warning banner */
    .stAlert {
        color: #000000 !important;
    }
    .stAlert > div {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="entry-title">{entry["title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="entry-date">{entry["date"]} {entry["time"]}</div>', unsafe_allow_html=True)

    # Summary section with header inside the box
    st.markdown(f'''
    <div class="content-box">
        <div class="section-header">Summary</div>
        {entry["summary"]}
    </div>
    ''', unsafe_allow_html=True)
    
    # Key Insights section with header inside the box
    insights_html = ''.join([f'<div class="bullet-point">• {insight}</div>' for insight in entry["key_insights"]])
    st.markdown(f'''
    <div class="content-box">
        <div class="section-header">Key Insights</div>
        {insights_html}
    </div>
    ''', unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Journal Entry", layout="wide")
    
    # Get entry_id from URL parameters using the new st.query_params
    entry_id = int(st.query_params.get("entry_id", "0"))
    
    entry = load_entry(entry_id)
    if entry:
        display_entry(entry)
    else:
        st.error("Entry not found")

if __name__ == "__main__":
    main()
