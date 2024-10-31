import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from transformers import pipeline
from datetime import datetime, timedelta
import databricks.sql as sql
import util
import os
#from dotenv import load_dotenv, find_dotenv

# Database connection parameters
db_hostname = "dbc-15e7860d-511f.cloud.databricks.com"
http_path = "/sql/1.0/warehouses/55aa3d052fd78c53"
token = os.getenv("DATABRICKS_TOKEN")


def show_dashboard():
    # Database connection parameters

    st.markdown('<div class="main-header"><h1>Fraud Guard AI</h1></div>', unsafe_allow_html=True)
    columns1 = ["call_id", "call_start_time", "call_end_time", "Label"]
    df_pd = util.get_data_from_table("llm.synthetic_call_data", columns1, db_hostname, http_path, token)

    df_pd['call_start_time'] = pd.to_datetime(df_pd['call_start_time'])
    df_pd['call_end_time'] = pd.to_datetime(df_pd['call_end_time'])

    df_pd['call_duration'] = (df_pd['call_end_time']-df_pd['call_start_time']).dt.total_seconds()/60
    df_pd.rename(columns={'Label': 'fraud'}, inplace=True)

    columns2 = ["call_id", "lon", "lat"]
    df_locations_pd = util.get_data_from_table("llm.case_locations", columns2, db_hostname, http_path, token)
    
    # Customizable Date Range for Dashboard Data
    
    #st.header('Customizable Date Range')
    c1, c2 = st.columns(2)
    with c1:
        start_date = st.date_input('Start Date', datetime.now() - timedelta(days=30))
    with c2:
        end_date = st.date_input('End Date', datetime.now())

    if start_date < end_date:
        df_filtered_date = df_pd[(df_pd['call_start_time'].dt.date >= start_date) & (df_pd['call_start_time'].dt.date <= end_date)]
        # Convert timestamp to datetime
        st.header('Summary')
        total_calls = df_filtered_date.shape[0]
        fraud_cases = df_filtered_date[df_filtered_date['fraud'] == 1].shape[0]
        avg_call_duration = df_filtered_date['call_duration'].mean().round(2)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Calls", total_calls)
        with c2:
            st.metric("Fraud Cases", fraud_cases)
        with c3:
            st.metric("Average Call Duration (s)", avg_call_duration)

        # Fraud Detection Rate Over the Last 7 Days
        col1, col2 = st.columns(2)
        
        daily_fraud_rate = df_filtered_date.groupby(df_filtered_date['call_start_time'].dt.date)['fraud'].mean().reset_index()
        fig = px.line(daily_fraud_rate, x='call_start_time', y='fraud', title='Daily Fraud Detection Rate')
        with col1:
            st.plotly_chart(fig)
        
        # Geographic Distribution of Calls and Fraud 
        agg_df = df_locations_pd.groupby(['lat', 'lon']).agg({'call_id': 'count'}).reset_index()
        fig = go.Figure(go.Scattergeo(
              lon = agg_df['lon'],
              lat = agg_df['lat'],
              locationmode = 'USA-states',
              mode = 'markers',
              marker = dict(
                  size = agg_df['call_id'],
                  color = 'red',
                  line = dict(width=1, color='rgb(40, 40, 40)'),
                  #sizemode = 'area'
              )))

        
        fig.update_layout(
             title = 'Geographic Distribution of Fruad Calls',
             #geo_scope='usa',
             geo=dict(
                 scope='usa',
                 landcolor = 'rgb(224, 240, 250)',
                 subunitcolor = 'rgb(40, 40, 40)',
                 countrycolor = 'rgb(40, 40, 40)',
             )
         )
        with col2:
            st.plotly_chart(fig)     
        
        # Call Volume Trends Over the Last 7 Days
        daily_call_volume = df_filtered_date.groupby(df_filtered_date['call_start_time'].dt.date)['call_id'].count().reset_index()
        fig = px.bar(daily_call_volume, x='call_start_time', y='call_id', title='Daily Call Volume')
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig)
        
        columns = ["call_id", "fraud_pattern"]
        df_pattern = util.get_data_from_table("llm.fraud_analysis_summary", columns, db_hostname, http_path, token)
        df_pattern['fraud_type'] = df_pattern['fraud_pattern'].str.split('/').str[0]
        agg_pattern = df_pattern.groupby(['fraud_type']).agg({'call_id': 'count'}).reset_index()
        top_10_df = agg_pattern.sort_values('call_id', ascending=False).head(5)

        with col2:
            # Pie Chart: Distribution of fraud alerts by region
            pie_chart_fig = px.pie(top_10_df, names='fraud_type', values='call_id', title='Top 5 Fraud Type')
            pie_chart_fig.update_layout(
                legend =dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.1,
                    xanchor="center",
                    x=0.5
                ) 
            )
            st.plotly_chart(pie_chart_fig)

        #recent_alerts = df_filtered_date[df_filtered_date['fraud'] == 1].tail(10)
        #st.header('Alerts and Notifications')
        #st.write(recent_alerts)


    else:
         st.error('Error: End date must fall after start date.')

#if __name__ == "__main__":
#    show_dashboard() 
