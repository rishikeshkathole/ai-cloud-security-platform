import streamlit as st
import boto3
import pandas as pd
import json
from datetime import datetime, timedelta

# AWS Clients
cloudwatch = boto3.client("cloudwatch", region_name="us-east-1")
cloudtrail = boto3.client("cloudtrail", region_name="us-east-1")
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# Streamlit Config
st.set_page_config(
    page_title="AI Cloud Security Platform",
    layout="wide"
)

# Title
st.title("🔐 AI-Powered Cloud Security & Incident Intelligence Platform")

# -----------------------------
# CLOUDWATCH METRICS
# -----------------------------

metrics = cloudwatch.get_metric_statistics(
    Namespace='AWS/EC2',
    MetricName='CPUUtilization',
    Dimensions=[
        {
            'Name': 'InstanceId',
            'Value': 'i-066899a4145f1c046'
        }
    ],
    StartTime=datetime.utcnow() - timedelta(hours=1),
    EndTime=datetime.utcnow(),
    Period=300,
    Statistics=['Average']
)

datapoints = metrics['Datapoints']

if datapoints:

    df = pd.DataFrame(datapoints)

    df = df.sort_values(by='Timestamp')

    latest_cpu = df['Average'].iloc[-1]

    col1, col2 = st.columns(2)

    with col1:
        st.metric("EC2 CPU Utilization", f"{latest_cpu:.2f}%")

    with col2:
        if latest_cpu > 70:
            st.error("⚠️ High CPU Usage Detected")
        else:
            st.success("✅ Infrastructure Healthy")

    st.subheader("📈 EC2 CPU Utilization Trend")
    st.line_chart(df.set_index('Timestamp')['Average'])

# -----------------------------
# CLOUDTRAIL EVENTS
# -----------------------------

st.subheader("🚨 Recent Security Events")

events = cloudtrail.lookup_events(
    StartTime=datetime.utcnow() - timedelta(hours=1),
    EndTime=datetime.utcnow(),
    MaxResults=5
)

event_list = []

for event in events['Events']:

    event_name = event.get("EventName", "Unknown")

    username = event.get("Username", "Unknown")

    event_time = event.get("EventTime")

    event_list.append({
        "Time": event_time,
        "User": username,
        "Event": event_name
    })

events_df = pd.DataFrame(event_list)

st.dataframe(events_df)

# -----------------------------
# AI INCIDENT ANALYSIS
# -----------------------------

st.subheader("🤖 AI Security Analysis")

incident_text = ""

for event in event_list:

    incident_text += f"""
    User: {event['User']}
    Event: {event['Event']}
    Time: {event['Time']}
    """

prompt = f"""
You are an AWS cloud security AI assistant.

Analyze these AWS CloudTrail events:

{incident_text}

Provide:
1. Security Risk Level
2. Possible Threats
3. Recommended Remediation
4. AWS Security Best Practices
"""

body = {
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "text": prompt
                }
            ]
        }
    ],
    "inferenceConfig": {
        "max_new_tokens": 500,
        "temperature": 0.5
    }
}

try:

    response = bedrock.invoke_model(
        modelId="amazon.nova-lite-v1:0",
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    response_body = json.loads(response["body"].read())

    ai_output = response_body["output"]["message"]["content"][0]["text"]

    st.success("✅ AI Analysis Generated")

    st.write(ai_output)

except Exception as e:

    st.error(f"Bedrock Error: {str(e)}")

# -----------------------------
# FOOTER
# -----------------------------

st.markdown("---")
st.caption("Built with AWS CloudWatch, CloudTrail, Bedrock, SNS, EventBridge, Streamlit, and Python")
