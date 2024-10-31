# databricks_hackathon

Intelligent Defense: Real-Time Fraud Detection with GenAI and Databricks

## Executive Summary
• Telecom fraud is a significant global issue, costing the industry over $28 billion annually through tactics like subscription fraud and account takeovers.
• Despite the implementation of advanced technologies, fraudsters are continually adapting, increasing the sophistication of their schemes.
• Leveraging cutting-edge GenAI technologies—such as tagging, classification, summarization, and Retrieval-Augmented Generation (RAG)—within the Databricks platform offers a powerful defense, enabling real-time, scalable, and accurate fraud detection and notification.
• Databricks' seamless deployment capabilities, coupled with user-friendly front-end tools like Streamlit, streamline the development and deployment of comprehensiv

## Objective 
  Develop a sophisticated fraud detection and prevention system for call interactions to enhance security, improve customer service quality, and provide actionable insights into fraudulent activities through advanced technologies and user-driven feedback mechanisms.

## Key Features:

  ### Fraud Report Dashboard:
  - Create a comprehensive dashboard visualizing historical call data to identify and analyze fraud patterns and trends. This feature provides detailed reports and visual analytics, enabling strategic decision-making and proactive fraud prevention.
  ### Real-Time Fraud Detection and Notification:
  - Implement real-time monitoring to detect fraudulent activities as they occur, with instant notifications to alert stakeholders, ensuring immediate intervention and risk mitigation.
  ### Call Transcription and Summarization:
  - Summarize call transcription to highlight critical information, aiding in fraud pattern detection with clear explanations.
  ### Call Sentiment Analysis:
  - Analyze the sentiment of calls for both customers and agents to detect anomalies indicating fraudulent behavior. Sentiment scores and trends provide early warnings of potential fraud.
  ### User Feedback Mechanism:
  - Develop a user review portal for thorough call reviews and detailed feedback. Comment Section: Leave specific comments and suggestions for agents and the CSR team.

## List of Databricks tools used

• Workspace
  1. git integration

• Catalog
  1. Load data
  2. Register RAG index and model 

• SQL
  1. Create Schema and tables for data organization

• Pyspark
  1. Perform data cleaning operations
  2. operate data ETL (Extract, Transform, Load)

• Databricks LLM Model: databricks-meta-llm-3-1-70b-instruct
  1. Data Synthesis: Generate synthetic data as needed
  2. Summarization: Summarize large volumes of text data
  3. Sentiment Analysis: Analyze the sentiment of text data to understand emotional tone
  4. Pattern recognization: Identify the fraud pattern from the transcript
 
• MLflow
  1. Register pipelines for model management and tracking

• Serving
  1. Create a serving endpoint for Retrieval-Augmented Generation (RAG) to deploy the model and make it accessible for real-time inference
 
• Databricks Apps
  1. Streamlit framework

## Presentation
    https://dbc-15e7860d-511f.cloud.databricks.com/editor/files/1108890155243782?o=2333727827300183


## Conclusion
  This project aims to build an advanced fraud detection and prevention system that identifies and mitigates fraudulent activities in real-time and provides valuable insights and feedback to improve overall customer service. By harnessing advanced technologies and user engagement, the app will offer a robust solution to safeguard call interactions and enhance organizational efficiency.

 
