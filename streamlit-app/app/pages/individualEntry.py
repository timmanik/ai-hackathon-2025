import streamlit as st
import sys
import os
from datetime import datetime
from urllib.parse import parse_qs

# Add the db directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../db')))
from app import app, JournalEntry

def load_entry(entry_id):
    """Load and return a specific entry by ID from database"""
    with app.app_context():
        try:
            entry = JournalEntry.query.get(entry_id)
            if entry:
                return {
                    "title": entry.title,
                    "date": entry.datetime_created.strftime("%Y-%m-%d"),
                    "time": entry.datetime_created.strftime("%H:%M"),
                    "summary": entry.summary,
                    "key_insights": entry.key_insights.split('\n') if entry.key_insights else [],
                    "transcription": entry.transcription
                }
            return None
        except Exception as e:
            st.error(f"Error loading entry from database: {str(e)}")
            return None

def display_entry(entry):
    """Display a single entry with its full content"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,700&display=swap');
    
    .stApp {
        background-color: #f7f1eb;
        color: #2b1810;
    }
    .yap-title {
        position: absolute;
        top: 20px;
        font-size: 32px;
        font-family: 'Fraunces', serif !important;
        font-weight: bold;
        color: #2b1810;
        z-index: 9999;
        background-color: transparent;
        cursor: pointer;
    }
    /* Override Streamlit's default text colors */
    .stMarkdown, .stText, p, span, div {
        color: #2b1810 !important;
    }
    .entry-title {
        font-size: 2.5rem;
        font-family: 'Fraunces', serif !important;
        font-weight: bold;
        margin-top: 80px;
        margin-bottom: 0.5rem;
        color: #2b1810;
    }
    .entry-date {
        font-style: italic;
        color: #2b1810;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-family: 'Fraunces', serif !important;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #2b1810;
    }
    .content-box {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #2b1810;
    }
    .bullet-point {
        margin-bottom: 0.5rem;
        color: #2b1810;
    }
    /* Style for the warning banner */
    .stAlert {
        color: #2b1810 !important;
    }
    .stAlert > div {
        color: #2b1810 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Add the yap! title with link
    st.markdown('<a href="/" class="yap-title">yap!</a>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="entry-title">{entry["title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="entry-date">{entry["date"]} {entry["time"]}</div>', unsafe_allow_html=True)


    # Summary section
    st.markdown(f'''
    <div class="content-box">
        <div class="section-header">Summary</div>
        {entry["summary"]}
    </div>
    ''', unsafe_allow_html=True)
    
    # Key Insights section
    insights_html = ''.join([f'<div class="bullet-point">• {insight.strip()}</div>' for insight in entry["key_insights"]])
    st.markdown(f'''
    <div class="content-box">
        <div class="section-header">Key Insights</div>
        {insights_html}
    </div>
    ''', unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Journal Entry", layout="wide")
    
    # Get entry_id from URL parameters
    try:
        entry_id = int(st.query_params.get("entry_id", "0"))
        entry = load_entry(entry_id)
        if entry:
            display_entry(entry)
        else:
            st.error(f"Entry with ID {entry_id} not found")
    except ValueError:
        st.error("Invalid entry ID")
    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
