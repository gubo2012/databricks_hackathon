# Databricks notebook source
# DBTITLE 1,Install Dependencies
# MAGIC %pip install mlflow==2.10.1 langchain==0.1.5 databricks-vectorsearch==0.22 databricks-sdk==0.18.0 mlflow[databricks]
# MAGIC %pip install databricks-cli
# MAGIC
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Set needed parameters
import os

DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

# host = "https://" + spark.conf.get("spark.databricks.workspaceUrl")
# os.environ['DATABRICKS_TOKEN'] = dbutils.secrets.get(scope="demo", key="azure3-token")

index_name="workspace.default.vs_index"
host = "https://" + spark.conf.get("spark.databricks.workspaceUrl")

VECTOR_SEARCH_ENDPOINT_NAME="hackathon_vs_endpoint"

# COMMAND ----------

# DBTITLE 1,Build Retriever
from databricks.vector_search.client import VectorSearchClient
from langchain_community.vectorstores import DatabricksVectorSearch
from langchain_community.embeddings import DatabricksEmbeddings

embedding_model = DatabricksEmbeddings(endpoint="databricks-bge-large-en")

def get_retriever(persist_dir: str = None):
    os.environ["DATABRICKS_HOST"] = host
    #Get the vector search index
    # vsc = VectorSearchClient(workspace_url=host, personal_access_token=os.environ["DATABRICKS_TOKEN"])
    vsc = VectorSearchClient(workspace_url=host, personal_access_token=DATABRICKS_TOKEN)
    vs_index = vsc.get_index(
        endpoint_name=VECTOR_SEARCH_ENDPOINT_NAME,
        index_name=index_name
    )

    # Create the retriever
    vectorstore = DatabricksVectorSearch(
        vs_index, text_column="content", embedding=embedding_model
    )
    return vectorstore.as_retriever()



# COMMAND ----------

# DBTITLE 1,Create the RAG Langchain
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatDatabricks

chat_model = ChatDatabricks(endpoint="databricks-dbrx-instruct", max_tokens = 200)

TEMPLATE = """You are an expert in telecommunication industry.Please determine the probability of fraud from the transcript between telecom agent and customer. Also summarize the fraud pattern, explanation, and summary if you think this transcript is fraud. Please make the result as concise as possible. The output is json format.

Use the following pieces of context to answer the question at the end:
{context}
Question: {question}
Answer:
"""

prompt = PromptTemplate(template=TEMPLATE, input_variables=["context", "question"])
# prompt = PromptTemplate(template=TEMPLATE)

chain = RetrievalQA.from_chain_type(
    llm=chat_model,
    chain_type="stuff",
    retriever=get_retriever(),
    chain_type_kwargs={"prompt": prompt}
)



# COMMAND ----------

# DBTITLE 1,Test Langchain
question = {"query": """Is this a telecom fraud? Customer Service Representative (CSR):
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
You’re welcome! Thank you for being a [Provider Name] customer. Have a great day!"""}
answer = chain.run(question)
print(answer)

# COMMAND ----------

# DBTITLE 1,Register our Chain as a model to Unity Catalog
from mlflow.models import infer_signature
import mlflow
import langchain

mlflow.set_registry_uri("databricks-uc")
model_name = "workspace.llm.app_fraud_run"

with mlflow.start_run(run_name="app_fraud_run") as run:
    signature = infer_signature(question, answer)
    model_info = mlflow.langchain.log_model(
        chain,
        loader_fn=get_retriever,  # Load the retriever with DATABRICKS_TOKEN env as secret (for authentication).
        artifact_path="chain",
        registered_model_name=model_name,
        pip_requirements=[
            "mlflow==" + mlflow.__version__,
            "langchain==" + langchain.__version__,
            "databricks-vectorsearch",
        ],
        input_example=question,
        signature=signature
    )

# COMMAND ----------

# Register the model to create a new version
from mlflow.tracking import MlflowClient

client = MlflowClient()
model_uri = f"runs:/{run.info.run_id}/chain"
new_model_version = client.create_model_version(
    name=model_name,
    source=model_uri,
    run_id=run.info.run_id
)

print(f"New model version: {new_model_version.version}")

# COMMAND ----------

# MAGIC %md
# MAGIC Deploying Model as a Serverless Model Endpoint

# COMMAND ----------

# Create or update serving endpoint
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import EndpointCoreConfigInput, ServedModelInput, ServedModelInputWorkloadSize
# from databricks.sdk.service.serving import EndpointCoreConfigInput, ServedEntityInput


serving_endpoint_name = f"fraud_app_endpoint_workspace_llm"
# latest_model_version = get_latest_model_version(model_name)
latest_model_version = new_model_version.version

w = WorkspaceClient()
endpoint_config = EndpointCoreConfigInput(
    name=serving_endpoint_name,
    served_models=[
        ServedModelInput(
            model_name=model_name,
            model_version=latest_model_version,
            workload_size=ServedModelInputWorkloadSize.SMALL, # Use string for workload size
            scale_to_zero_enabled=True,
            environment_vars={
                "DATABRICKS_TOKEN": DATABRICKS_TOKEN,  # <scope>/<secret> that contains an access token
            }
        )
    ]
)

existing_endpoint = next(
    (e for e in w.serving_endpoints.list() if e.name == serving_endpoint_name), None
)
if existing_endpoint is None:
    print(f"Creating the endpoint {serving_endpoint_name}, this will take a few minutes to package and deploy the endpoint...")
    w.serving_endpoints.create_and_wait(name=serving_endpoint_name, config=endpoint_config)
else:
    print(f"Updating the endpoint {serving_endpoint_name} to version {latest_model_version}, this will take a few minutes to package and deploy the endpoint...")
    w.serving_endpoints.update_config_and_wait(served_models=endpoint_config.served_models, name=serving_endpoint_name)

# COMMAND ----------

question = """Is this a telecom fraud? Customer Service Representative (CSR):
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
You’re welcome! Thank you for being a [Provider Name] customer. Have a great day!"""

answer = w.serving_endpoints.query(serving_endpoint_name, inputs=[{"query": question}])
print(answer.predictions[0])

# COMMAND ----------

import requests
import json

local_endpoint = "https://dbc-15e7860d-511f.cloud.databricks.com/serving-endpoints/fraud_app_endpoint_workspace_llm/invocations"
headers = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}
payload = {
    "inputs": [{"query": question}]
}

response = requests.post(local_endpoint, headers=headers, data=json.dumps(payload))
print(response.json())
