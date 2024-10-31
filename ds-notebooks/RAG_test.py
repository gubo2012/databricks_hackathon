# Databricks notebook source
# MAGIC %md
# MAGIC This example is to test RAG serving endpoint.

# COMMAND ----------

conversation = """ CCR: you for calling [Company Name]. My name is [Representative Name]. How can I assist you today?
FC: Hi, I need to change the SIM card on my phone. I lost my phone and I need a new SIM activated.
CCR: I'm sorry to hear that you lost your phone. I'd be happy to assist you with that. For security purposes, can you please verify your account information? I'll need your full name, address, and the last four digits of your Social Security number.

FC: Sure, my name is John Smith, my address is 123 Main Street, Anytown, USA, and the last four digits of my Social are 1234.

CCR: Thank you, John. I appreciate your cooperation. Can you also provide me with the account passcode or PIN?

FC: Oh, I don't remember setting a passcode. Could you reset it for me?

CCR: Unfortunately, I can't reset the passcode without proper verification. Let me ask you a few security questions based on your account information. What is your mother's maiden name?

FC: It's Johnson.

CCR: Thank you. That matches our records. I will now send a one-time PIN to the phone number listed on your account. Please provide me with the code once you receive it.

FC: Actually, I don't have access to that number since I lost my phone. Can you send it to my email instead?

CCR: For security reasons, we can only send the one-time PIN to the phone number on file. Is there any other way you can access your old phone number?

FC: No, I can't access it. Can we skip this step? I really need to get this done quickly.

CCR: I understand your urgency, but we must follow our verification process to protect your account. If you can't receive the one-time PIN, we have to verify your identity in person at one of our stores.

FC: This is really inconvenient. I just need to get my new SIM working. I have all my details. Isn't there another way?

CCR: I'm afraid not, sir. Our verification process is in place for your security. If you visit one of our stores with a valid ID, they can assist you further.

FC: Fine, I’ll go to a store. Thanks for nothing.

CCR: I'm sorry for the inconvenience, but your security is our top priority. Have a good day."""

# COMMAND ----------

question = {"query": conversation}

# COMMAND ----------

import requests
import json
import os

host = "https://" + spark.conf.get("spark.databricks.workspaceUrl")
os.environ['DATABRICKS_TOKEN'] = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

local_endpoint = 'https://dbc-15e7860d-511f.cloud.databricks.com/serving-endpoints/fraud_app_rag_endpoint_dev/invocations'
headers = {
    "Authorization":  f"Bearer {os.environ['DATABRICKS_TOKEN']}",
    "Content-Type": "application/json"
}

payload = {
    "inputs": [{"query": question}]
}
response = requests.post(local_endpoint, headers=headers, data=json.dumps(payload))
response_json = response.json()
print(response_json)

# COMMAND ----------

# DBTITLE 1,unit test
def is_fraudulent(transcription, url):
    local_endpoint = url
    headers = {
        "Authorization": f"Bearer {os.environ['DATABRICKS_TOKEN']}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": [{"query": transcription}]
    }

    response = requests.post(local_endpoint, headers=headers, data=json.dumps(payload))
    # print(response.json())
    # Assuming response is an HTTP response object you've received
    response_json = response.json()  # This already gives you a Python dictionary
    data = response_json['predictions'][0]  # Directly access the data
    data_dict = json.loads(data)

    # print(data_dict)
    # print(data['fraud probability score'])
    return {
        "is_fraudulent": data_dict['fraud probability score'],
        "explanation": data_dict['explanation']
    }

# COMMAND ----------

serving_endpoint = 'https://dbc-15e7860d-511f.cloud.databricks.com/serving-endpoints/fraud_app_rag_endpoint_dev/invocations'
is_fraudulent(transcription=conversation, url=serving_endpoint)

# COMMAND ----------


