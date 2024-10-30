import streamlit as st
import numpy as np
from sklearn.ensemble import IsolationForest
import smtplib
from email.mime.text import MIMEText
from openai import OpenAI
import pandas as pd
import os
import time

import util

db_hostname = "dbc-15e7860d-511f.cloud.databricks.com"
http_path = "/sql/1.0/warehouses/55aa3d052fd78c53"
token = os.environ.get("DATABRICKS_TOKEN")

client = OpenAI(
  api_key=token,
  base_url="https://dbc-15e7860d-511f.cloud.databricks.com/serving-endpoints"
)

# Function to simulate streaming data
def simulate_streaming_data_gpt(client, num_call=1):
    data = [util.generate_fake_call(client) for _ in range(num_call)]
    return data


# Fraud detection function
def is_fraudulent(transcription):
    fraudulent_keywords = ["free", "win", "prize", "urgent"]
    return any(keyword in transcription.lower() for keyword in fraudulent_keywords)

 
def detect_anomalies(data):
    model = IsolationForest(contamination=0.1)
    model.fit(data)
    predictions = model.predict(data)
    anomalies = data[predictions == -1]
    return anomalies

# Function to send email alert
def send_email_alert(anomalies):
    # Email configuration
    sender_email = "kf3527@att.com"
    receiver_email = "kf3527@att.com"
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
    data_placeholder = st.empty()
    # Simulate and display streaming data
    for _ in range(3):
        new_data = simulate_streaming_data_gpt(client, 1)
        df = pd.DataFrame(new_data).reset_index(drop=True).rename(columns={0: "transcription"})
        
        # Perform fraud
        df["is_fraudulent"] = df["transcription"].apply(is_fraudulent)
        #df["fradulent_highlight"] = df["is_fraudulent"].apply(lambda x: "background: red" if x else '')

        styled_df = df.style.apply(lambda x: df["fradulent_highlight"], axis=1)

        #st.table(styled_df)

        # Update the DataFrame in the Streamlit app
        data_placeholder.dataframe(df)
        #st.dataframe(df)
        # Wait for a few seconds before generating the next batch
        time.sleep(30)
        # Convert input to a list of integers
        #data = np.array([int(x) for x in interaction_logs.split(",")]).reshape(-1, 1)
        # Detect anomalies
        #anomalies = detect_anomalies(data)
 
        #if len(anomalies) > 0:
        #    st.error("Fraud Alert! Anomalies detected.")
        #    st.write("Anomalous Data Points:")
        #    st.write(anomalies)
            # Send email alert
            #send_email_alert(anomalies)
        #else:
        #    st.success("No anomalies detected.")