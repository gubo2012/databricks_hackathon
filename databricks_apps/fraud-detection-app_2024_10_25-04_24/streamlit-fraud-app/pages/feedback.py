import streamlit as st
import pandas as pd
from databricks import sql
import util
from datetime import datetime
import plotly.express as px

# Database connection details
db_hostname = "dbc-15e7860d-511f.cloud.databricks.com"
http_path = "/sql/1.0/warehouses/55aa3d052fd78c53"
token = os.environ.get("DATABRICKS_TOKEN")
tablename = "llm.synthetic_call_data"

def show_feedback():
    # Streamlit app
    st.markdown('<div class="main-header"><h1>Fraud Detection Feedback Review</h1></div>', unsafe_allow_html=True)
    st.write("This page allows agents to review and provide feedback on potential fraud cases.")



    # Columns to fetch
    columns = ['call_id', 'agent_notes', 'transcription', 'Label']

    if "call_id" not in st.session_state:
        st.session_state["call_id"] = ""

    # Fetch data from the database
    call_id = st.text_input("Enter Call ID...")
    st.session_state["call_id"] = call_id

    df = util.get_data_from_table("llm.synthetic_call_data", columns, db_hostname, http_path, token)

    if not df.empty and st.session_state["call_id"] != "":
        # Display case details
        case_details = df[df['call_id'] == call_id].iloc[0]
        st.subheader(f"Details for Call ID: {call_id}")
        st.write(f"Previously Labeled as Fraud: {case_details['Label']}")
        with st.expander("Previous Call Details"):
            st.write(f"Previous Call Details: {case_details['transcription']}")

        # Layout with columns
        col1, col2 = st.columns(2)

        # Feedback form
        with col1:
            st.subheader("Provide Your Feedback")
            feedback = st.text_area("Feedback", case_details['agent_notes'])
            feedback_fraud = st.selectbox("Is this case fraudulent?", [True, False])
            uid = "aa1111"
            dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if st.button("Submit Feedback"):
                util.save_feedback_to_db(call_id, feedback, feedback_fraud, uid, dt, db_hostname, http_path, token)
        # Analysis results
        with col2:
            st.subheader("Previous Feedback Analysis Results")
            # Fetch and visualize feedback distribution
            feedback_df = util.get_data_from_table("llm.feedback", ['fraud'], db_hostname, http_path, token)
            if not feedback_df.empty:
                feedback_counts = feedback_df['fraud'].value_counts()
                feedback_counts_df = pd.DataFrame(feedback_counts).reset_index()
                feedback_counts_df.columns = ['Fraud', 'Count']
                #st.bar_chart(feedback_counts)
                fig = px.bar(feedback_counts_df, x='Fraud', y='Count', title='Feedback Distribution')
                st.plotly_chart(fig)
    else:
        st.error("No data available to display.")

    

