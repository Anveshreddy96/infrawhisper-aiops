import boto3
import json
import os
import re

bedrock = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION_NAME', 'us-east-1'))

def invoke_claude(prompt):

    model_id = os.environ.get('BEDROCK_MODEL', 'us.anthropic.claude-sonnet-4-6')

    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4000,
        "temperature": 0.1,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    print(f"Calling Bedrock with model: {model_id}")

    response = bedrock.invoke_model(
        modelId = model_id,
        body    = json.dumps(request_body)
    )

    response_body = json.loads(response['body'].read().decode('utf-8'))
    claude_reply  = response_body['content'][0]['text']

    print(f"Claude replied: {claude_reply[:200]}...")

    try:
        clean_reply = re.sub(r'```(?:json)?\s*', '', claude_reply)
        clean_reply = clean_reply.replace('```', '').strip()
        analysis    = json.loads(clean_reply)

    except json.JSONDecodeError:
        print("Warning: Claude did not reply in JSON format. Using default.")
        analysis = {
            "severity"   : "P2",
            "summary"    : "Alarm fired — manual review needed",
            "root_cause" : claude_reply,
            "impact"     : "Unknown — review manually",
            "runbook"    : "1. Check CloudWatch metrics\n2. Review application logs\n3. Escalate if needed",
            "prevention" : "Review alarm thresholds"
        }

    return analysis
