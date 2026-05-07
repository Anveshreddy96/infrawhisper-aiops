import boto3
import uuid
import json
import os
from datetime import datetime, timezone

# This connects to DynamoDB using the AWS SDK (boto3)
# It reads the table name from environment variable we set in Terraform
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION_NAME', 'us-east-1'))

def save_incident(alarm_name, alarm_details, ai_analysis):
    """
    This function saves one incident record to DynamoDB.
    
    alarm_name    = name of the CloudWatch alarm that fired
    alarm_details = full details of the alarm (metric, threshold etc)
    ai_analysis   = what Claude said about this incident
    """

    # Get the DynamoDB table name from environment variable
    table_name = os.environ.get('DYNAMODB_TABLE', 'infrawhisper-incidents')
    table = dynamodb.Table(table_name)

    # Create a unique ID for this incident
    # uuid4() generates a random unique string like: "a1b2c3d4-e5f6-..."
    incident_id = str(uuid.uuid4())

    # Get current time in ISO format like: "2025-05-07T10:30:00+00:00"
    timestamp = datetime.now(timezone.utc).isoformat()

    # Build the incident record — this is what gets stored in DynamoDB
    incident = {
        'incident_id'  : incident_id,       # unique ID (primary key)
        'timestamp'    : timestamp,          # when it happened
        'alarm_name'   : alarm_name,         # which alarm fired
        'alarm_details': json.dumps(alarm_details),  # full alarm info as text
        'severity'     : ai_analysis.get('severity', 'UNKNOWN'),   # P1/P2/P3
        'root_cause'   : ai_analysis.get('root_cause', 'UNKNOWN'), # what caused it
        'runbook'      : ai_analysis.get('runbook', 'UNKNOWN'),    # how to fix it
        'summary'      : ai_analysis.get('summary', 'UNKNOWN'),    # short summary
        'status'       : 'OPEN'             # all new incidents start as OPEN
    }

    # Actually save it to DynamoDB
    table.put_item(Item=incident)

    # Print to CloudWatch logs so we can debug if needed
    print(f"Incident saved: {incident_id} | Alarm: {alarm_name} | Severity: {incident['severity']}")

    # Return the incident so other code can use it
    return incident
