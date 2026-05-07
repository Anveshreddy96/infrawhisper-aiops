import json
import os
from prompt_builder import build_prompt
from bedrock_client import invoke_claude
from incident_model import save_incident

def lambda_handler(event, context):
    """
    This is the MAIN function Lambda calls when an alarm fires.
    
    event   = the alarm data sent by EventBridge (what alarm fired, details etc)
    context = Lambda runtime info (we don't use this but it's required)
    
    Flow:
    1. Read the alarm details from the event
    2. Build a prompt for Claude
    3. Call Claude and get analysis
    4. Save everything to DynamoDB
    5. Return the result
    """

    print("InfraWhisper Lambda triggered!")
    print(f"Raw event received: {json.dumps(event)}")

    try:
        # ── STEP 1: Extract alarm details from the event ──────────────────
        # EventBridge sends alarm data in event['detail']
        # If we are testing manually, we handle that too
        
        if 'detail' in event:
            # Real CloudWatch alarm coming through EventBridge
            detail      = event['detail']
            alarm_name  = detail.get('alarmName', 'Unknown Alarm')
            state       = detail.get('state', {})
            config      = detail.get('configuration', {})
            metrics     = config.get('metrics', [{}])
            
            # Extract metric details safely
            metric_stat = metrics[0].get('metricStat', {}) if metrics else {}
            metric      = metric_stat.get('metric', {})

            alarm_details = {
                'metric_name'   : metric.get('name', 'Unknown'),
                'namespace'     : metric.get('namespace', 'Unknown'),
                'threshold'     : config.get('description', 'Unknown'),
                'current_value' : state.get('reasonData', 'Unknown'),
                'state'         : state.get('value', 'ALARM'),
                'region'        : event.get('region', 'us-east-1'),
                'account_id'    : event.get('account', 'Unknown')
            }

        elif 'alarm_name' in event:
            # Manual test event — we sent this ourselves for testing
            alarm_name    = event['alarm_name']
            alarm_details = {
                'metric_name'   : event.get('metric_name', 'CPUUtilization'),
                'namespace'     : event.get('namespace', 'AWS/EC2'),
                'threshold'     : event.get('threshold', '80%'),
                'current_value' : event.get('current_value', '95%'),
                'state'         : 'ALARM',
                'region'        : event.get('region', 'us-east-1'),
                'account_id'    : event.get('account_id', '123456789')
            }

        else:
            # Unknown event format — use defaults so Lambda doesn't crash
            alarm_name    = 'Unknown Alarm'
            alarm_details = {
                'metric_name'   : 'Unknown',
                'namespace'     : 'Unknown',
                'threshold'     : 'Unknown',
                'current_value' : 'Unknown',
                'state'         : 'ALARM',
                'region'        : 'us-east-1',
                'account_id'    : 'Unknown'
            }

        print(f"Processing alarm: {alarm_name}")
        print(f"Alarm details: {json.dumps(alarm_details)}")

        # ── STEP 2: Build the prompt for Claude ───────────────────────────
        # This calls prompt_builder.py and creates the message for Claude
        print("Building prompt for Claude...")
        prompt = build_prompt(alarm_name, alarm_details)

        # ── STEP 3: Call Claude AI via Bedrock ────────────────────────────
        # This calls bedrock_client.py which sends prompt to Claude
        print("Calling Claude AI via Bedrock...")
        ai_analysis = invoke_claude(prompt)
        print(f"AI Analysis received: {json.dumps(ai_analysis)}")

        # ── STEP 4: Save everything to DynamoDB ───────────────────────────
        # This calls incident_model.py which saves to DynamoDB
        print("Saving incident to DynamoDB...")
        incident = save_incident(alarm_name, alarm_details, ai_analysis)

        # ── STEP 5: Return success response ───────────────────────────────
        print(f"SUCCESS! Incident {incident['incident_id']} processed.")

        return {
            'statusCode' : 200,
            'body'       : json.dumps({
                'message'     : 'Incident processed successfully',
                'incident_id' : incident['incident_id'],
                'alarm_name'  : alarm_name,
                'severity'    : ai_analysis.get('severity', 'UNKNOWN'),
                'summary'     : ai_analysis.get('summary', 'UNKNOWN'),
                'root_cause'  : ai_analysis.get('root_cause', 'UNKNOWN'),
                'runbook'     : ai_analysis.get('runbook', 'UNKNOWN')
            })
        }

    except Exception as e:
        # If anything goes wrong, print the error and return failure
        # This prevents Lambda from silently failing
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

        return {
            'statusCode' : 500,
            'body'       : json.dumps({
                'message' : 'Error processing incident',
                'error'   : str(e)
            })
        }
