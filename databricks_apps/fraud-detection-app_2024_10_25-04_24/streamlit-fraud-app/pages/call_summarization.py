import streamlit as st
from openai import OpenAI
import util
import re
import json_repair
import os

db_hostname = "dbc-15e7860d-511f.cloud.databricks.com"
http_path = "/sql/1.0/warehouses/55aa3d052fd78c53"
token = os.environ.get("DATABRICKS_TOKEN")

client = OpenAI(
  api_key=token,
  base_url="https://dbc-15e7860d-511f.cloud.databricks.com/serving-endpoints"
)

def show_call_summarization():

    st.markdown('<div class="main-header"><h1>Call Summarization</h1></div>', unsafe_allow_html=True)
    st.write("This feature generates summaries of customer calls using Generative AI.")

    # Columns to fetch
    cols = ['call_id', 'transcription']

    if "call_id" not in st.session_state:
        st.session_state["summarization"] = ""

    # Fetch data from the database
    call_id = st.text_input("Enter Call ID...")
    st.session_state["summarization"] = call_id

    found = False 
    summary_df = util.get_data_from_table("llm.synthetic_call_data", cols, db_hostname, http_path, token)

    if not summary_df.empty and st.session_state["summarization"] != "":
        if call_id in summary_df['call_id'].values:
            found = True
            case_details = summary_df[summary_df['call_id'] == call_id].iloc[0]
            with st.expander("Call Details"):
                st.write(f"Call Details: {case_details['transcription']}")

        if found and st.button("Generate Summary"):
            # Placeholder for AI model integration
            summary = util.generate_summary(case_details['transcription'], client)

            # Extract JSON part from the result
            json_start = summary.find('{')
            json_end = summary.rfind('}') + 1
            json_str = summary[json_start:json_end]
            result_data = json_repair.loads(json_str)
            st.json(result_data)
  
            # Extracting the keywords using regular expressions
            fraud_probability = result_data['fraud_probability']
            fraud_pattern = result_data['fraud_pattern']
            explanation = result_data['Explanation']
            summary_txt = result_data['Summary']

            #save_summarization_to_db(call_id, fraud_probability, fraud_pattern, explanation, summary_txt)

    else:
        st.error("No data available to display.")
