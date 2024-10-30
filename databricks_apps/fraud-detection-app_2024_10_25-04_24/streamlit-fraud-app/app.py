import streamlit as st
from streamlit_navigation_bar import st_navbar

# Importing functions from separate files
from pages.dashboard import show_dashboard
from pages.real_time_detection import show_real_time_detection
from pages.call_summarization import show_call_summarization
from pages.sentiment_analysis import show_sentiment_analysis
from pages.feedback import show_feedback

# Page configuration
pages = ["Home",  "Realtime Fraud Detection", "Call Summarization", "Sentiment Analysis", "Feedback", "GitHub"]
urls = {"GitHub": "https://github.com/gubo2012/databricks_hackathon"}

# Custom CSS and JS for enhanced UI
st.markdown(
    """
    <style>
    /* General Styles */
    body {
        font-family: 'Roboto', sans-serif;
        background-color: #f4f4f9;
    }

    /* Sidebar Styles */
    .sidebar .sidebar-content {
        background-color: #007bff;
        color: #fff;
    }
    .sidebar .sidebar-content a {
        color: #fff;
        text-decoration: none;
    }
    .sidebar .sidebar-content a:hover {
        text-decoration: underline;
    }

    /* Button Styles */
    .stButton>button {
        background-color: #009FDB;
        color: #fff;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
 
    /* Main Content Styles */
    .main-content {
        text-align: center;
        margin-bottom: 40px;
    }
    .main-content h1 {
        font-size: 2.5em;
    }
    .main-content p {
        font-size: 1.2em;
        color: #333;
    }

    /* Footer Styles */
    .footer {
        background-color: #007bff;
        color: #fff;
        text-align: center;
        padding: 20px;
    }
    .footer a {
        color: #fff;
        text-decoration: none;
    }
    .footer a:hover {
        text-decoration: underline;
    }
    </style>
 
    <script>
    function toggleTheme() {
        var element = document.body;
        element.classList.toggle("dark-mode");
    }
    </script>
    """,
    unsafe_allow_html=True,
)

styles = {
    "nav": {
        "background-color": "#009FDB",
        "justify-content": "left",
    },
    "img": {
        "padding-right": "14px",
    },
    "span": {
        "color": "white",
        "padding": "14px",
    },
    "active": {
        "color": "var(--text-color)",
        "background-color": "white",
        "font-weight": "normal",
        "padding": "14px",
    }
}
options = {
    "show_menu": False,
    "show_sidebar": False,
}
page = st_navbar(
    pages,
    urls=urls,
    styles=styles,
    options=options,
)
functions = {
    "Home": show_dashboard,
    'Realtime Fraud Detection': show_real_time_detection,
    'Call Summarization': show_call_summarization,
    'Sentiment Analysis': show_sentiment_analysis,
    'Feedback': show_feedback,
}

go_to = functions.get(page)
if go_to:
    go_to()

