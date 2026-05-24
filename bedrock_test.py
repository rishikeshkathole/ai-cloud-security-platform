import boto3
import json

# Bedrock Runtime Client
bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

# Prompt
prompt = """
You are an AWS cloud monitoring assistant.

Analyze this infrastructure activity:
Several unsuccessful sign-in attempts were observed from unusual locations.

Provide:
1. Risk level
2. Possible reason
3. Suggested best practices
4. Recommended AWS security improvements
"""

# Correct Nova Request Format
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
        "max_new_tokens": 300,
        "temperature": 0.5
    }
}

# Invoke Model
response = bedrock.invoke_model(
    modelId="amazon.nova-lite-v1:0",
    body=json.dumps(body),
    contentType="application/json",
    accept="application/json"
)

# Read Response
response_body = json.loads(response["body"].read())

# Print Output
print("\n===== AI SECURITY ANALYSIS =====\n")

print(
    response_body["output"]["message"]["content"][0]["text"]
)
