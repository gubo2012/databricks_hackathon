import streamlit as st
from openai import OpenAI
import util
import re
import json
import json_repair
import os


db_hostname = "dbc-15e7860d-511f.cloud.databricks.com"
http_path = "/sql/1.0/warehouses/55aa3d052fd78c53"
token = os.getenv("DATABRICKS_TOKEN")

client = OpenAI(
  api_key=token,
  base_url="https://dbc-15e7860d-511f.cloud.databricks.com/serving-endpoints"
)

def show_sentiment_analysis():

    st.markdown('<div class="main-header"><h1>Sentiment Analysis</h1></div>', unsafe_allow_html=True)
    st.write("This feature analyzes the sentiment of the call")

    # Columns to fetch
    cols = ['call_id', 'transcription']

    if "call_id" not in st.session_state:
        st.session_state["sentiment"] = ""

    # Fetch data from the database
    call_id = st.text_input("Enter Call ID...")
    st.session_state["sentiment"] = call_id
    
    found = False
    summary_df = util.get_data_from_table("llm.synthetic_call_data", cols, db_hostname, http_path, token)

    if not summary_df.empty and st.session_state["sentiment"] != "":
        # Check if call ID exists
        if call_id in summary_df['call_id'].values:
            found = True
            case_details = summary_df[summary_df['call_id'] == call_id].iloc[0]
            with st.expander("Call Details"):
                st.write(f"Call Details: {case_details['transcription']}")
        else:
            st.error("Call ID not found.")
       
        if found and st.button("Analyze Sentiment"):
            with st.spinner("Analyzing..."):
                result = util.sentiment_analysis(case_details['transcription'], client)
            
            # Extract JSON part from the result
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            json_str = result[json_start:json_end]
            result_data = json_repair.loads(json_str)
            st.json(result_data)
            
            # Save to table
            util.save_sentiment_to_db(call_id, result_data, db_hostname, http_path, token)

    else:
        st.error("No data available to display.")
