import streamlit as st
import os
import pandas as pd
import databricks.sql as sql
from openai import OpenAI
import json

# Function to connect to Databricks and fetch customer data
def get_data_from_table(tablename, columns, db_hostname, http_path, token):
    try:
        with sql.connect(
            server_hostname=db_hostname,
            http_path=http_path,
            access_token=token
        ) as connection:
            with connection.cursor() as cursor:
                columns_str = ", ".join(columns)
                query = f"SELECT distinct {columns_str} FROM {tablename}"
                cursor.execute(query)
                result = cursor.fetchall()
                df = pd.DataFrame(result, columns=columns)
                return df
    except Exception as e:
        st.error(f"Failed to retrieve data: {tablename} {e}")
    
    
# Function to connect to Databricks and w customer data
def save_feedback_to_db(call_id, note, fraud, uid, update_time, db_hostname, http_path, token):
    try:
        with sql.connect(
            server_hostname=db_hostname,
            http_path=http_path,
            access_token=token
        ) as connection:
            with connection.cursor() as cursor:
                query = f"INSERT INTO llm.feedback (call_id, note, fraud, uid, update_time) VALUES ('{call_id}', '{note}', {fraud}, '{uid}', '{update_time}')"
                cursor.execute(query)
            connection.close()
            st.info("Feedback saved successfully")
    except Exception as e:
        st.error(f"Failed to save data: {e}")


    
# Function to connect to Databricks and w customer data
def save_sentiment_to_db(call_id, data, db_hostname, http_path, token):
    #data["agent_sentiment"],
    #data["agent_explanation"])
    try:
        with sql.connect(
            server_hostname=db_hostname,
            http_path=http_path,
            access_token=token
        ) as connection:
            with connection.cursor() as cursor:
                query = f"INSERT INTO llm.sentiment_analysis (call_id, customer_sentiment, customer_explanation,    agent_sentiment, agent_explanation) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (
                    call_id,
                    data["customer_sentiment"], 
                    data["customer_explanation"],
                    data["agent_sentiment"],
                    data["agent_explanation"]
                ))
            connection.close()
            st.info("Feedback saved successfully")
    except Exception as e:
        st.error(f"Failed to save data: {e}")



def generate_summary(call_transcript, client):
    try:
        chat_completion = client.chat.completions.create(
        messages=[
        {
            "role": "system",
            "content":
            """You are an expert in telecommunication industry.Please determine the probability of fraud from the transcript between telecom agent and customer. Also summarize the fraud pattern, explanation, and summary if you think this transcript is fraud. Please make the result as concise as possible. The output is json format.
            
            Example:
            {
            fraud_probability: 0.8
            fraud_pattern: "Phishing/Identity Theft"
            Explanation: 
                * The customer (FC) claims to have received a notification about suspicious activity, which could be a legitimate concern. However, the agent (CCR) asks for sensitive information such as the customer's Social Security number and account passcode, which is not standard practice for verification.
                * The customer provides personal details, but when asked for the account passcode, they claim to have forgotten it. Instead of offering to reset the passcode or providing alternative verification methods, the customer asks the agent to disclose sensitive information (email or phone number on file), which could be an attempt to gather more personal data.
            Summary:
                This pattern is indicative of a phishing or identity theft attempt, where the scammer is trying to gather sensitive information by posing as a telecom agent. The probability of fraud is high (0.8) due to the unusual request for sensitive information and the customer's suspicious behavior.
            }
            """
        },
        {
            "role": "user",
            "content":f"""{call_transcript}"""
        }
        ],
        model="databricks-meta-llama-3-1-70b-instruct",
        max_tokens=512
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Failed to generate summary: {e}")


def sentiment_analysis(call_transcript, client):
    try:
        chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content":
                """You are an expert in sentiment analysis. Please analyze the sentiment of the following call transcript between a telecom agent and a customer. Provide separate sentiment scores (positive, neutral, negative) and brief explanations for both the customer and the agent. The output should be in JSON format.

            
                Example:
                {
                    "customer_sentiment": "positive",
                    "customer_explanation": "The customer expresses satisfaction with the service and appreciates the agent's assistance.",
                    "agent_sentiment": "neutral",
                    "agent_explanation": "The agent maintains a professional tone throughout the call."
                }
                """
            },
            {
                "role": "user",
                "content": f"""{call_transcript}"""
            }
        ],

        model="databricks-meta-llama-3-1-70b-instruct",
        max_tokens=512
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Failed to Sentiment Analysis: {e}")


def generate_fake_call(client):
    try:
        chat_completion = client.chat.completions.create(
        messages=[
        {
            "role": "system",
            "content":
            """You are a helpful assistant that geanerats fake call transcriptions""" 
        },
        {
            "role": "user",
            "content":  """Generate a fake call transcription between a customer and telecom call center agent.
                The transcription should be around 150-200 characters long.
                Don't include Call date and Call time in the output.
                Include different type fraud call randomly. Don't show this "Here is a fake call transcription" in the output""" 
        }
        ],
        model="databricks-meta-llama-3-1-70b-instruct",
        max_tokens=512
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        return f"Failed to generate fake call: {e}"