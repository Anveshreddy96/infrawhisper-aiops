import boto3
import json
import os
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

# APIRouter is like a mini-app that holds related endpoints
# We group all incident-related endpoints here
router = APIRouter()

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION_NAME', 'us-east-1'))
table    = dynamodb.Table(os.getenv('DYNAMODB_TABLE', 'infrawhisper-incidents'))

# ── ENDPOINT 1 ────────────────────────────────────────────────────────────────
# GET /incidents
# Returns list of all incidents stored in DynamoDB
@router.get("/incidents")
def get_all_incidents():
    """
    Returns all incidents from DynamoDB.
    Most recent first.
    """
    try:
        # Scan means "get everything from the table"
        response = table.scan()
        items    = response.get('Items', [])

        # Sort by timestamp — newest first
        items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return {
            "total"     : len(items),
            "incidents" : items
        }

    except Exception as e:
        # If something goes wrong, return a proper error
        raise HTTPException(status_code=500, detail=str(e))


# ── ENDPOINT 2 ────────────────────────────────────────────────────────────────
# GET /incidents/{incident_id}
# Returns one specific incident by its ID
@router.get("/incidents/{incident_id}")
def get_incident(incident_id: str):
    """
    Returns one incident by incident_id.
    Example: GET /incidents/7d2a090d-dbb1-4f4a-9e27-d199a7f1f858
    """
    try:
        response = table.get_item(
            Key={'incident_id': incident_id}
        )

        # get_item returns 'Item' if found, nothing if not found
        item = response.get('Item')

        if not item:
            raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

        return item

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── ENDPOINT 3 ────────────────────────────────────────────────────────────────
# POST /incidents/simulate
# Manually triggers a fake alarm → Lambda → Claude → DynamoDB
# This is your DEMO endpoint to show recruiters!
@router.post("/incidents/simulate")
def simulate_incident(
    alarm_name    : str = "High-CPU-Production-Server",
    metric_name   : str = "CPUUtilization",
    namespace     : str = "AWS/EC2",
    threshold     : str = "80%",
    current_value : str = "95%"
):
    """
    Simulates a CloudWatch alarm by directly calling Lambda.
    Use this to demo the AIOps system without waiting for real alarms.
    """
    try:
        # Call Lambda directly using boto3
        lambda_client = boto3.client('lambda', region_name=os.getenv('AWS_REGION_NAME', 'us-east-1'))

        # Build the test payload — same format Lambda expects
        payload = {
            "alarm_name"    : alarm_name,
            "metric_name"   : metric_name,
            "namespace"     : namespace,
            "threshold"     : threshold,
            "current_value" : current_value,
            "region"        : os.getenv('AWS_REGION_NAME', 'us-east-1'),
            "account_id"    : "demo-account"
        }

        # Invoke Lambda function
        response = lambda_client.invoke(
            FunctionName    = os.getenv('LAMBDA_FUNCTION', 'infrawhisper-triage-engine'),
            InvocationType  = 'RequestResponse',  # wait for response
            Payload         = json.dumps(payload)
        )

        # Read Lambda's response
        result = json.loads(response['Payload'].read().decode('utf-8'))
        body   = json.loads(result.get('body', '{}'))

        return {
            "message"     : "Simulation triggered successfully",
            "incident_id" : body.get('incident_id'),
            "alarm_name"  : alarm_name,
            "severity"    : body.get('severity'),
            "summary"     : body.get('summary')
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── ENDPOINT 4 ────────────────────────────────────────────────────────────────
# GET /health
# Simple health check — confirms API is running
@router.get("/health")
def health_check():
    return {
        "status"    : "healthy",
        "service"   : "InfraWhisper API",
        "timestamp" : datetime.now(timezone.utc).isoformat()
    }
