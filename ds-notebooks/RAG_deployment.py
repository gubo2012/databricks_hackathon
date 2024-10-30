# Databricks notebook source
# DBTITLE 1,Install Dependencies
# MAGIC %pip install mlflow==2.10.1 langchain==0.1.5 databricks-vectorsearch==0.22 databricks-sdk==0.18.0 mlflow[databricks]
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Set needed parameters
import os

host = "https://" + spark.conf.get("spark.databricks.workspaceUrl")
os.environ['DATABRICKS_TOKEN'] = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

index_name="workspace.llm.fraud_docs_index"
host = "https://" + spark.conf.get("spark.databricks.workspaceUrl")

VECTOR_SEARCH_ENDPOINT_NAME="vector_search_endpoint"

# COMMAND ----------

# DBTITLE 1,Build Retriever
from databricks.vector_search.client import VectorSearchClient
from langchain_community.vectorstores import DatabricksVectorSearch
from langchain_community.embeddings import DatabricksEmbeddings

embedding_model = DatabricksEmbeddings(endpoint="databricks-bge-large-en")

def get_retriever(persist_dir: str = None):
    os.environ["DATABRICKS_HOST"] = host
    #Get the vector search index
    vsc = VectorSearchClient(workspace_url=host, personal_access_token=os.environ["DATABRICKS_TOKEN"])
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

TEMPLATE = """You are an fraud investigator. You are identifying if a conversation between CCR(agent) and FC(customer) are fraudulent. Provide the answer and the probability score of being fraud.
Use the following pieces of context to answer the question at the end:
{context}
Question: {question}
Answer:
"""
prompt = PromptTemplate(template=TEMPLATE, input_variables=["context", "question"])

chain = RetrievalQA.from_chain_type(
    llm=chat_model,
    chain_type="stuff",
    retriever=get_retriever(),
    chain_type_kwargs={"prompt": prompt}
)



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

# DBTITLE 1,Test Langchain
question = {"query": conversation}
answer = chain.run(question)
print(answer)

# COMMAND ----------

# DBTITLE 1,Register our Chain as a model to Unity Catalog
from mlflow.models import infer_signature
import mlflow
import langchain

mlflow.set_registry_uri("databricks-uc")
model_name = "workspace.llm.rag"

with mlflow.start_run(run_name="rag_run") as run:
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

# Create or update serving endpoint
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import EndpointCoreConfigInput, ServedModelInput, ServedModelInputWorkloadSize
# from databricks.sdk.service.serving import EndpointCoreConfigInput, ServedEntityInput


serving_endpoint_name = "fraud_app_rag_endpoint"
# latest_model_version = get_latest_model_version(model_name)
latest_model_version = '2'

w = WorkspaceClient()
endpoint_config = EndpointCoreConfigInput(
    name=serving_endpoint_name,
    served_models=[
        ServedModelInput(
            model_name=model_name,
            model_version = latest_model_version,
            workload_size=ServedModelInputWorkloadSize.SMALL, # Use string for workload size
            scale_to_zero_enabled=True,
            environment_vars={
                "DATABRICKS_TOKEN": os.environ['DATABRICKS_TOKEN']  # <scope>/<secret> that contains an access token
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

import requests
import json
local_endpoint = 'https://dbc-15e7860d-511f.cloud.databricks.com/serving-endpoints/fraud_app_rag_endpoint/invocations'
headers = {
    "Authorization":  f"Bearer {os.environ['DATABRICKS_TOKEN']}",
    "Content-Type": "application/json"
}
payload = {
    "inputs": [{"query": question}]
}
response = requests.post(local_endpoint, headers=headers, data=json.dumps(payload))
print(response.json())
