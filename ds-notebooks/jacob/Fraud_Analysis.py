# Databricks notebook source
# MAGIC %pip install openpyxl
# MAGIC # Upgrade the typing_extensions package
# MAGIC %pip install --upgrade typing_extensions
# MAGIC
# MAGIC # Install the openai package
# MAGIC %pip install openai
# MAGIC
# MAGIC %pip install json-repair
# MAGIC
# MAGIC # Restart the Python kernel to ensure the new packages are used
# MAGIC dbutils.library.restartPython()
# MAGIC
# MAGIC

# COMMAND ----------

import pandas as pd

# Read the Excel file
file_path = "/Workspace/Users/bg337a@att.com/databricks_hackathon/data/fraud_tactics.xlsx"
fraud_df = pd.read_excel(file_path, sheet_name=1)

# Convert to CSV and save
# csv_file_path = "/Workspace/Users/bg337a@att.com/databricks_hackathon/data/fraud_tactics.csv"
# fraud_df.to_csv(csv_file_path, index=False)

# Display the first 20 rows of the dataframe
fraud_df.head(20)

# COMMAND ----------

# transcript_sample = fraud_df.loc[1, 'transcription']

# COMMAND ----------

# MAGIC %md
# MAGIC ### prompt engineering

# COMMAND ----------

# from openai import OpenAI
# import os

# # How to get your Databricks token: https://docs.databricks.com/en/dev-tools/auth/pat.html
# # DATABRICKS_TOKEN = os.environ.get('DATABRICKS_TOKEN')
# # Alternatively in a Databricks notebook you can use this:
# DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

# client = OpenAI(
#   api_key=DATABRICKS_TOKEN,
#   base_url="https://dbc-15e7860d-511f.cloud.databricks.com/serving-endpoints"
# )

# chat_completion = client.chat.completions.create(
#   messages=[
#   {
#     "role": "system",
#     "content": "You are an AI assistant"
#   },
#   {
#     "role": "user",
#     "content": "Tell me about Large Language Models"
#   }
#   ],
#   model="databricks-meta-llama-3-1-70b-instruct",
#   max_tokens=256
# )

# print(chat_completion.choices[0].message.content)

# COMMAND ----------

from openai import OpenAI
import os
import json

# How to get your Databricks token: https://docs.databricks.com/en/dev-tools/auth/pat.html
# DATABRICKS_TOKEN = os.environ.get('DATABRICKS_TOKEN')
# Alternatively in a Databricks notebook you can use this:
DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

client = OpenAI(
  api_key=DATABRICKS_TOKEN,
  base_url="https://dbc-15e7860d-511f.cloud.databricks.com/serving-endpoints"
)

fraud_results = {}
for index, row in fraud_df.iterrows():
    if index>=0:
        print(index)
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
            "content":f"""{row['transcription']}"""
        }
        ],
        model="databricks-meta-llama-3-1-70b-instruct",
        max_tokens=512
        )

        fraud_results[row['call_id']] = chat_completion.choices[0].message.content

    else:
        break


# COMMAND ----------

fraud_results_df = pd.DataFrame.from_dict(
    fraud_results, 
    orient='index'
).reset_index(drop=False)

fraud_results_df = fraud_results_df.rename({'index': 'caller_id', 0: 'fraud_analysis'}, axis=1)
fraud_results_df.to_csv("/Workspace/Users/jz3477@att.com/fraud_analysis.csv")

# COMMAND ----------

fraud_results_df = pd.read_csv("/Workspace/Users/jz3477@att.com/fraud_analysis.csv", index_col=False)

# COMMAND ----------

fraud_results_df = fraud_results_df.drop(['Unnamed: 0'], axis=1)

# COMMAND ----------

import json_repair

final_dict = {}
for index, row in fraud_results_df.iterrows():
    data_str = fraud_results_df.loc[index, 'fraud_analysis']
    json_start = data_str.find('{')
    json_end = data_str.rfind('}') + 1
    json_str = data_str[json_start:json_end]
    data_dict = json_repair.loads(json_str)
    final_dict[row['caller_id']] = data_dict
    print(f"{index} done!")

# COMMAND ----------

fraud_final_df =pd.DataFrame.from_dict(final_dict).transpose().reset_index(drop=False)[['index', 'fraud_probability', 'fraud_pattern', 'Explanation', 'Summary']]
fraud_final_df.rename({'index': 'caller_id'}, axis=1, inplace=True)

# COMMAND ----------

fraud_final_df.to_csv("/Workspace/Users/jz3477@att.com/fraud_analysis_final.csv", index=False)

# COMMAND ----------

import json
import json_repair

data_str = fraud_results_df.loc[0, 'fraud_analysis']
json_start = data_str.find('{')
json_end = data_str.rfind('}') + 1
json_str = data_str[json_start:json_end]
data_dict = json_repair.loads(json_str)


# json_str = json_str.strip()
# json_str = json_str.replace('\n', '')
# data_dict = json.loads(json_str)

print(json.dumps(data_dict, indent=2))

# COMMAND ----------

# MAGIC %md
# MAGIC ##### test examples

# COMMAND ----------

from openai import OpenAI
import os

# How to get your Databricks token: https://docs.databricks.com/en/dev-tools/auth/pat.html
# DATABRICKS_TOKEN = os.environ.get('DATABRICKS_TOKEN')
# Alternatively in a Databricks notebook you can use this:
DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

client = OpenAI(
  api_key=DATABRICKS_TOKEN,
  base_url="https://dbc-15e7860d-511f.cloud.databricks.com/serving-endpoints"
)

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
    "content":f"""{transcript_sample}"""
  }
  ],
  model="databricks-meta-llama-3-1-70b-instruct",
  max_tokens=512
)

print(chat_completion.choices[0].message.content)

# COMMAND ----------

from openai import OpenAI
import os

# How to get your Databricks token: https://docs.databricks.com/en/dev-tools/auth/pat.html
# DATABRICKS_TOKEN = os.environ.get('DATABRICKS_TOKEN')
# Alternatively in a Databricks notebook you can use this:
DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

client = OpenAI(
  api_key=DATABRICKS_TOKEN,
  base_url="https://dbc-15e7860d-511f.cloud.databricks.com/serving-endpoints"
)

chat_completion = client.chat.completions.create(
  messages=[
  {
    "role": "system",
    "content": "You are an expert in telecommunication industry.Please determine the probability of fraud from the transcript between telecom agent and customer. Also summarize the fraud pattern if you think this transcript is fraud."
  },
  {
    "role": "user",
    "content": 
        """Customer Service Representative (CSR):
Thank you for calling [Provider Name], my name is Jessica. How can I help you today?

Scammer (SC):
Hi Jessica, I need to remove a line from my account. My kid doesn't need the phone anymore, and I want to cancel that line.

CSR:
I can assist with that. Could I have your account number or phone number associated with the account to get started?

SC:
Sure, the account number is 98765432, and the main number is 555-123-4567.

CSR:
Thank you. Now, for security purposes, I’ll need to verify the account. Can you provide me with the account PIN?

SC:
Ah, yes. The PIN should be 2468.

CSR:
It looks like that PIN isn’t correct. Don’t worry, I can send you a one-time verification code to your phone. Would that work for you?

SC:
Oh, I’m actually calling from a different phone because I lost my main one. That’s one of the reasons I’m trying to simplify things on my account. Is there any other way I can verify? I have my billing info, my address, and I can answer any security questions you have.

CSR:
I understand. Since you’re not able to receive a text, I can send the verification code to your email address. Would you like me to do that?

SC:
Hmm, I’m currently traveling, and I can’t access my email either. It’s been a bit of a hassle this week. But I’m the account holder—John Miller. I have my ID and all my personal details if you need that.

CSR:
We generally need to verify through either phone or email for security reasons. Let me check if there are any alternate contacts or methods on file for your account.

SC:
Actually, I think there’s another number listed on my account—555-987-6543. That’s my spouse’s phone. You could send the verification code there, and I can confirm it right now.

CSR:
Let me check that. Yes, I do see that number as an authorized contact on your account. I’ll send the verification code there now.

SC:
Great! Just a second... Got it. The code is 392718.

CSR:
Thank you for confirming that! Your account is now verified. Let me know which line you’d like to remove.

SC:
I want to remove the number 555-456-7890 from the account, please.

CSR:
Alright, I see that number is currently active on your plan. By removing it, the number will be deactivated immediately, and you’ll no longer be billed for it. Would you like to proceed?

SC:
Yes, please go ahead and remove it.

CSR:
The line has been successfully removed from your account. Is there anything else I can assist you with today?

SC:
No, that’s all. Thanks for your help!

CSR:
You’re welcome! Thank you for being a [Provider Name] customer. Have a great day!
"""
  }
  ],
  model="databricks-meta-llama-3-1-70b-instruct",
  max_tokens=512
)

print(chat_completion.choices[0].message.content)

# COMMAND ----------

from openai import OpenAI
import os

# How to get your Databricks token: https://docs.databricks.com/en/dev-tools/auth/pat.html
# DATABRICKS_TOKEN = os.environ.get('DATABRICKS_TOKEN')
# Alternatively in a Databricks notebook you can use this:
DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

client = OpenAI(
  api_key=DATABRICKS_TOKEN,
  base_url="https://dbc-15e7860d-511f.cloud.databricks.com/serving-endpoints"
)

chat_completion = client.chat.completions.create(
  messages=[
  {
    "role": "system",
    "content": "You are an expert in telecommunication industry.Please determine the probability of fraud from the transcript between telecom agent and customer. Also summarize the fraud pattern if you think this transcript is fraud."
  },
  {
    "role": "user",
    "content": 
        """Agent:
Thank you for calling [Telecom Company]. This is Sarah. How can I assist you today?

Fake Customer:
Hi, Sarah. I need to port my number to a different carrier. I just switched, and they told me to contact you to initiate the process.

Agent:
Sure, I can help with that! Can you please provide me with the phone number you want to port?

Fake Customer:
Yes, it's 555-123-4567. I need to get this done as quickly as possible. It’s urgent.

Agent:
No problem, I’ll get this started for you. To verify your identity, could you please confirm the account holder's full name and the last four digits of the Social Security Number?

Fake Customer:
Uh, yeah, the name is John Davis, and the last four of the SSN are 6789.

Agent:
Thank you, Mr. Davis. For security reasons, I’ll also need to ask for the PIN on your account or the answer to your security question. Which would you prefer?

Fake Customer:
Oh, right, I don’t remember the PIN. I don’t use it that much. But I can answer the security question. What is it?

Agent:
No worries! Your security question is: "What’s the name of your first pet?"

Fake Customer:
Uh, it was... Sparky. Yeah, Sparky!

Agent:
Hmm, unfortunately, that answer doesn’t match what we have on file. Are you sure you’d like to try again?

Fake Customer:
Oh, yeah, sorry about that. I forgot—it's been a while. Can I just reset the PIN or something?

Agent:
I understand the urgency, but for security reasons, we’ll need to verify your identity first before resetting the PIN or processing the port-out request. Do you have access to the email or phone number associated with this account so we can send a verification code?

Fake Customer:
Actually, I don’t have access to that phone right now. It’s lost—that’s why I’m trying to port the number out so I can use my new phone. Couldn’t you just process it based on my info?

Agent:
I’m really sorry, but we can’t proceed without verifying your identity through multiple security checks. This is to protect the account holder from unauthorized changes. If you don’t have access to the phone or email, you’ll need to visit a store with a valid ID for further assistance.

Fake Customer:
This is ridiculous! I’m telling you, it’s my account! I just need this done. I’ll take my business elsewhere if this isn’t resolved.

Agent:
I understand your frustration, but we take customer security very seriously. If you can get access to the email or visit a store with ID, we’ll be happy to help. Is there anything else I can assist you with?

Fake Customer:
No, thanks. I’ll figure it out.

Agent:
Alright. If you need further assistance, please feel free to reach out. Have a great day!
"""
  }
  ],
  model="databricks-meta-llama-3-1-70b-instruct",
  max_tokens=512
)

print(chat_completion.choices[0].message.content)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Embedding Model

# COMMAND ----------

# from openai import OpenAI
# import os

# # How to get your Databricks token: https://docs.databricks.com/en/dev-tools/auth/pat.html
# # DATABRICKS_TOKEN = os.environ.get('DATABRICKS_TOKEN')
# # Alternatively in a Databricks notebook you can use this:
# DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

# client = OpenAI(
#   api_key=DATABRICKS_TOKEN,
#   base_url="https://dbc-15e7860d-511f.cloud.databricks.com/serving-endpoints"
# )

# embeddings = client.embeddings.create(
#   input='Your string for the embedding model goes here',
#   model="databricks-gte-large-en"
# )

# print(embeddings.data[0].embedding)

# COMMAND ----------

from openai import OpenAI
import os

# How to get your Databricks token: https://docs.databricks.com/en/dev-tools/auth/pat.html
# DATABRICKS_TOKEN = os.environ.get('DATABRICKS_TOKEN')
# Alternatively in a Databricks notebook you can use this:
DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

client = OpenAI(
  api_key=DATABRICKS_TOKEN,
  base_url="https://dbc-15e7860d-511f.cloud.databricks.com/serving-endpoints"
)

embeddings = client.embeddings.create(
  input="""Agent:
Thank you for calling [Telecom Company]. This is Sarah. How can I assist you today?

Fake Customer:
Hi, Sarah. I need to port my number to a different carrier. I just switched, and they told me to contact you to initiate the process.

Agent:
Sure, I can help with that! Can you please provide me with the phone number you want to port?

Fake Customer:
Yes, it's 555-123-4567. I need to get this done as quickly as possible. It’s urgent.

Agent:
No problem, I’ll get this started for you. To verify your identity, could you please confirm the account holder's full name and the last four digits of the Social Security Number?

Fake Customer:
Uh, yeah, the name is John Davis, and the last four of the SSN are 6789.

Agent:
Thank you, Mr. Davis. For security reasons, I’ll also need to ask for the PIN on your account or the answer to your security question. Which would you prefer?

Fake Customer:
Oh, right, I don’t remember the PIN. I don’t use it that much. But I can answer the security question. What is it?

Agent:
No worries! Your security question is: "What’s the name of your first pet?"

Fake Customer:
Uh, it was... Sparky. Yeah, Sparky!

Agent:
Hmm, unfortunately, that answer doesn’t match what we have on file. Are you sure you’d like to try again?

Fake Customer:
Oh, yeah, sorry about that. I forgot—it's been a while. Can I just reset the PIN or something?

Agent:
I understand the urgency, but for security reasons, we’ll need to verify your identity first before resetting the PIN or processing the port-out request. Do you have access to the email or phone number associated with this account so we can send a verification code?

Fake Customer:
Actually, I don’t have access to that phone right now. It’s lost—that’s why I’m trying to port the number out so I can use my new phone. Couldn’t you just process it based on my info?

Agent:
I’m really sorry, but we can’t proceed without verifying your identity through multiple security checks. This is to protect the account holder from unauthorized changes. If you don’t have access to the phone or email, you’ll need to visit a store with a valid ID for further assistance.

Fake Customer:
This is ridiculous! I’m telling you, it’s my account! I just need this done. I’ll take my business elsewhere if this isn’t resolved.

Agent:
I understand your frustration, but we take customer security very seriously. If you can get access to the email or visit a store with ID, we’ll be happy to help. Is there anything else I can assist you with?

Fake Customer:
No, thanks. I’ll figure it out.

Agent:
Alright. If you need further assistance, please feel free to reach out. Have a great day!""",
  model="databricks-gte-large-en"
)

print(embeddings.data[0].embedding)

# COMMAND ----------


