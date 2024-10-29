# Databricks notebook source
# %pip install -U --quiet databricks-sdk==0.28.0 databricks-agents mlflow-skinny mlflow mlflow[gateway] databricks-vectorsearch langchain==0.2.1 langchain_core==0.2.5 langchain_community==0.2.4

%pip install lxml==4.9.3 transformers==4.30.2 langchain==0.0.344 databricks-vectorsearch==0.22
dbutils.library.restartPython()


# COMMAND ----------

# %run ./_resources/00-init $reset_all_data=false

# COMMAND ----------

import pandas as pd
from pyspark.sql.functions import *
from pyspark.sql.types import *

# COMMAND ----------

data_path = '/Workspace/Users/bg337a@att.com/databricks_hackathon/data/fraud_tactics.csv'

fraud_df = pd.read_csv('/Workspace/Users/bg337a@att.com/databricks_hackathon/data/fraud_tactics.csv').drop('Unnamed: 4',axis = 1).rename(columns ={'Fraud Tactics':'fraud_tactics'})
#fraud_df = spark.createDataFrame(df)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Splitting conversation in smaller chunks

# COMMAND ----------

# DBTITLE 1,Splitting conversation in smaller chunks
from langchain.text_splitter import HTMLHeaderTextSplitter, RecursiveCharacterTextSplitter
from transformers import AutoTokenizer

max_chunk_size = 500

# Function to split conversation into chunks based on speaker turns
def split_conversation(conversation, max_chunk_size=500):
    # Split the conversation by lines
    lines = conversation.split("\n")
    chunks = []
    current_chunk = []

    for line in lines:
        # Check if the line starts with a speaker identifier and the current chunk is not empty
        if (line.startswith("CCR:") or line.startswith("FC:")) and current_chunk:
            # Join the current chunk into one string and add it to the chunks list
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
        else:
            # Add the line to the current chunk
            current_chunk.append(line)
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append("\n".join(current_chunk))
    
    return chunks

# Define a pandas UDF to apply the splitting function to a Spark DataFrame column
#@pandas_udf("array<string>")
def parse_and_split_conversation(docs: pd.Series) -> pd.Series:
    return docs.apply(lambda doc: split_conversation(doc, max_chunk_size=500))

 
# Let's try our chunking function
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

split_conversation(conversation)

fraud_df['split_conversations'] = parse_and_split_conversation(fraud_df['transcription'])

# fraud_df = fraud_df.withColumn("split_conversations", parse_and_split_conversation(col("transcription")))

# display(fraud_df)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Example: Using Databricks Foundation model BGE as an embedding endpoint

# COMMAND ----------

import mlflow.deployments
deploy_client = mlflow.deployments.get_deploy_client("databricks")

response = deploy_client.predict(endpoint="databricks-bge-large-en", inputs={"input": ["What is Apache Spark?",'mistake']})
embeddings = [e['embedding'] for e in response.data]
print(len(embeddings[0]))

# COMMAND ----------

# MAGIC %md
# MAGIC #### Create the final databricks_documentation table containing chunks

# COMMAND ----------

# MAGIC %sql
# MAGIC --Note that we need to enable Change Data Feed on the table to create the index
# MAGIC CREATE TABLE IF NOT EXISTS frauds_documentation (
# MAGIC   call_id STRING,
# MAGIC   agent_notes STRING,
# MAGIC   fraud_tactics STRING,
# MAGIC   content STRING,
# MAGIC   embedding ARRAY <FLOAT>
# MAGIC ) TBLPROPERTIES (delta.enableChangeDataFeed = true); 
# MAGIC
# MAGIC  -- id BIGINT GENERATED BY DEFAULT AS IDENTITY

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE EXTENDED frauds_documentation

# COMMAND ----------

# MAGIC %md
# MAGIC #### Computing the chunk embeddings and saving them to our Delta Table

# COMMAND ----------

import mlflow.deployments
deploy_client = mlflow.deployments.get_deploy_client("databricks")

#@pandas_udf("array<float>")
def get_embedding(contents: pd.Series) -> pd.Series:
    def get_embeddings(batch):
        #Note: this will gracefully fail if an exception is thrown during embedding creation (add try/except if needed) 
        response = deploy_client.predict(endpoint="databricks-bge-large-en", inputs={"input": batch})
        return [e['embedding'] for e in response.data]

    # Splitting the contents into batches of 150 items each, since the embedding model takes at most 150 inputs per request.
    max_batch_size = 150
    batches = [contents.iloc[i:i + max_batch_size] for i in range(0, len(contents), max_batch_size)]

    # Process each batch and collect the results
    all_embeddings = []
    for batch in batches:
        all_embeddings += get_embeddings(batch.tolist())

    return pd.Series(all_embeddings)

# COMMAND ----------

# embedding = (fraud_df
#       .withColumn('content', explode(parse_and_split_conversation('transcription'))))
# test = embedding.withColumn('embedding', get_embedding('content'))

#fraud_df_exploded = fraud_df.explode('split_conversations')
#fraud_df_exploded['embedding'] = get_embedding(fraud_df_exploded['split_conversations'])

fraud_df = fraud_df.rename(columns = {'transcription':'content'})
fraud_df['embedding'] = get_embedding(fraud_df['content'])


# COMMAND ----------

fraud_df.head()

# COMMAND ----------

schema = StructType([
    StructField('call_id',StringType()),
    StructField('content',StringType()), 
    StructField('agent_notes',StringType()), 
    StructField('fraud_tactics',StringType()),           
    StructField("embedding", ArrayType(FloatType(), containsNull=False), nullable=True),
])

# Assuming fraud_df is a Pandas DataFrame
fraud_docs = spark.createDataFrame(fraud_df, schema=schema)

fraud_docs.write.mode('overwrite').saveAsTable("frauds_documentation")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM frauds_documentation LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC #### Self-Managed Vector Search Index

# COMMAND ----------

 vsc.list_endpoints()['endpoints']

# COMMAND ----------

from databricks.vector_search.client import VectorSearchClient
vsc = VectorSearchClient()

VECTOR_SEARCH_ENDPOINT_NAME = 'test1'

if VECTOR_SEARCH_ENDPOINT_NAME not in [e['name'] for e in vsc.list_endpoints()['endpoints']]:
    vsc.create_endpoint(name = VECTOR_SEARCH_ENDPOINT_NAME, endpoint_type="STANDARD")

print(f"Endpoint named {VECTOR_SEARCH_ENDPOINT_NAME} is ready.")

# COMMAND ----------

existing_indexes = vsc.list_indexes('test1')
existing_indexes

# # Check if 'workspace.default.fraud_documentation_index' is in the list of existing indexes
# if 'workspace.default.fraud_documentation_index' in [index['name'] for index in existing_indexes['vector_indexes']]:
#     vsc.delete_index('test1', 'workspace.default.fraud_documentation_index')
#     print("Index deleted successfully.")
# else:
#     print("Index does not exist.")

# COMMAND ----------

vsc.delete_index('test1', 'workspace.default.fraud_docs')

# COMMAND ----------

from databricks.sdk import WorkspaceClient
import databricks.sdk.service.catalog as c

catalog = 'workspace'
db = 'default'
#The table we'd like to index
source_table_fullname = f"{catalog}.{db}.frauds_documentation"
# Where we want to store our index
vs_index_fullname = f"{catalog}.{db}.frauds_documentation_index"


print(f"Creating index {vs_index_fullname} on endpoint {VECTOR_SEARCH_ENDPOINT_NAME}...")
vsc.create_delta_sync_index(
  endpoint_name = 'test1',
  index_name = vs_index_fullname,
  source_table_name = source_table_fullname,
  pipeline_type="CONTINUOUS",
  primary_key="call_id",
  embedding_dimension=1024, #Match your model embedding size (bge)
  embedding_vector_column="embedding"
)

#Let's wait for the index to be ready and all our embeddings to be created and indexed
print(f"index {vs_index_fullname} on table {source_table_fullname} is ready")

# COMMAND ----------

index_info = vsc.get_index(VECTOR_SEARCH_ENDPOINT_NAME, vs_index_fullname)
index_info

# COMMAND ----------

import mlflow.deployments
deploy_client = mlflow.deployments.get_deploy_client("databricks")

question = "one time pin request"
response = deploy_client.predict(endpoint="databricks-bge-large-en", inputs={"input": [question]})
embeddings = [e['embedding'] for e in response.data]

results = vsc.get_index(VECTOR_SEARCH_ENDPOINT_NAME, vs_index_fullname).similarity_search(
  query_vector=embeddings[0],
  columns=["agent_notes", "content"],
  num_results=1)
docs = results.get('result', {}).get('data_array', [])
docs
