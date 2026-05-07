def build_prompt(alarm_name, alarm_details):
    """
    This function builds the message (prompt) we send to Claude AI.
    
    We give Claude:
    - The alarm name
    - All alarm details (metric, threshold, current value etc)
    
    We ask Claude to reply in JSON format so our code can easily read it.
    """

    # Extract useful info from the alarm details
    # .get() means "get this value, but if it doesn't exist use the default"
    metric_name      = alarm_details.get('metric_name', 'Unknown Metric')
    namespace        = alarm_details.get('namespace', 'Unknown Namespace')
    threshold        = alarm_details.get('threshold', 'Unknown')
    current_value    = alarm_details.get('current_value', 'Unknown')
    alarm_state      = alarm_details.get('state', 'ALARM')
    region           = alarm_details.get('region', 'us-east-1')
    account_id       = alarm_details.get('account_id', 'Unknown')

    # This is the actual message we send to Claude
    # We are very specific about what format we want back
    prompt = f"""You are an expert AWS DevOps Site Reliability Engineer (SRE) with deep knowledge of AWS services, monitoring, and incident response.

A CloudWatch alarm has just fired in a production AWS environment. Analyze this incident and provide a structured response.

INCIDENT DETAILS:
- Alarm Name: {alarm_name}
- Metric: {metric_name}
- Namespace: {namespace}
- Threshold Breached: {threshold}
- Current Value: {current_value}
- Alarm State: {alarm_state}
- AWS Region: {region}
- Account ID: {account_id}

Based on this alarm, provide your analysis in the following JSON format ONLY. Do not include any text outside the JSON:

{{
    "severity": "P1 or P2 or P3",
    "summary": "One sentence summary of what happened",
    "root_cause": "Detailed explanation of what likely caused this alarm to fire",
    "impact": "What systems or users are likely affected by this",
    "runbook": "Step by step actions the on-call engineer should take to investigate and resolve this",
    "prevention": "What changes should be made to prevent this in future"
}}

Severity Guide:
- P1 = Critical, production is down, immediate action needed
- P2 = High, significant degradation, action needed within 1 hour  
- P3 = Medium, minor issue, action needed within 24 hours

Respond with valid JSON only. No markdown, no explanation outside JSON."""

    return prompt
