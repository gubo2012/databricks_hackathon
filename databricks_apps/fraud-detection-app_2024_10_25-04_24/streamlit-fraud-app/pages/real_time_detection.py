import streamlit as st
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
import smtplib
from email.mime.text import MIMEText
from openai import OpenAI
import pandas as pd
import os
import time
import requests
import json
import util

db_hostname = "dbc-15e7860d-511f.cloud.databricks.com"
http_path = "/sql/1.0/warehouses/55aa3d052fd78c53"
token = os.environ.get("OPENAI_API_KEY")


client = OpenAI(
  api_key=token,
  base_url="https://dbc-15e7860d-511f.cloud.databricks.com/serving-endpoints"
)

# Function to simulate streaming data
def simulate_streaming_data_gpt(client):
    data = util.generate_fake_call(client)
    return data


# Fraud detection function
def is_fraudulent(transcription):
    local_endpoint = 'https://dbc-15e7860d-511f.cloud.databricks.com/serving-endpoints/fraud_app_rag_endpoint_dev/invocations'
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": [{"query": transcription}]
    }

    response = requests.post(local_endpoint, headers=headers, data=json.dumps(payload))
    print(response.json())
    response_json = response.json()
    data = response_json['predictions'][0]  # Directly access the data
    data_dict = json.loads(data)

    # print(data_dict)
    # print(data['fraud probability score'])
    return data_dict['fraud probability score'], data_dict['explanation']

def detect_anomalies(data):
    if isinstance(data, str):
        data = [data]

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(data)

    model = IsolationForest(contamination=0.1)
    model.fit(X.toarray())
              
    scores = model.decision_function(X.toarray())
    anomalies = model.predict(X.toarray())
    return scores, anomalies

# Function to send email alert
def send_email_alert(anomalies):
    # Email configuration
    sender_email = ""
    receiver_email = ""
    subject = "Fraud Alert!"
    body = f"Anomalies detected: {anomalies}"

    # Create email message
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    # Send email
    with smtplib.SMTP("smtp.att.com", 587) as server:
        server.starttls()
        server.login(sender_email, "your_password")
        server.sendmail(sender_email, receiver_email, msg.as_string())

# Main function for real-time detection page
def show_real_time_detection():
    st.markdown('<div class="main-header"><h1>Real-time Detection</h1></div>', unsafe_allow_html=True)
    st.write("This feature detects anomalies in real-time interactions, which could indicate potential fraud.")

    # Placeholder for the DataFrame
    # Simulate and display streaming data
    for _ in range(10):
        data_placeholder = st.empty()
        new_data = util.generate_fake_call(client)
    
        st.write(new_data)
        # Perform fraud
        fradulent_probability_score, explaination = is_fraudulent(new_data)

        #Detect anomalies
        anomaly_scores, anomalies = detect_anomalies(new_data)
        is_anomaly = anomalies[0] == -1


        # Highlight fraudulent interactions
        #df["fradulent_highlight"] = df.apply(lambda x: "background-color: red" if x["fradulent_probability_score"] > 0.5 or x["is_anomaly"] else "", axis=1)
        #styled_df = df.style.apply(lambda x: df["fradulent_highlight"], axis=1)

        # Wait for a few seconds before generating the next batch
 
        if is_anomaly or fradulent_probability_score > 0.5:
            st.error("Fraud Alert! Anomalies detected.")
            st.write("Anomalous Data Points:")
            st.write(explaination)
            # Send email alert
            #send_email_alert(df[df["is_anomaly"] | df["is_fraudulent"]].to_dict())
        else:
            st.success("No anomalies detected.")
        st.markdown("-----")
        time.sleep(5)
