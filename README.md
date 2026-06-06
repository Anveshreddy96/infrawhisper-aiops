# InfraWhisper - AIOps Incident Intelligence Platform

AI-powered incident triage using AWS Bedrock + Claude Sonnet 4.6

## What It Does

InfraWhisper automatically analyzes AWS CloudWatch alarms using Claude AI and generates:
- Root Cause Analysis - what caused the incident
- Severity Classification - P1 / P2 / P3
- Runbook - step-by-step resolution guide
- Impact Assessment - what systems are affected

## Architecture

CloudWatch Alarm → EventBridge → Lambda → AWS Bedrock (Claude Sonnet 4.6)
                                                    ↓
React Dashboard ← FastAPI ← DynamoDB ← AI Analysis

## Tech Stack

| Layer | Technology |
|---|---|
| AI Engine | AWS Bedrock - Claude Sonnet 4.6 |
| Compute | AWS Lambda (Python 3.11) |
| Event Routing | AWS EventBridge |
| Database | AWS DynamoDB |
| IaC | Terraform |
| API | FastAPI + Python |
| Frontend | React.js |
| Hosting | AWS EC2 |


## Project Structure

infrawhisper/
├── terraform/   - All AWS infrastructure as code
├── lambda/      - AI triage engine (Bedrock + Claude)
├── api/         - REST API (FastAPI)
└── dashboard/   - React frontend

## How to Deploy

1. Deploy Infrastructure
cd terraform
terraform init
terraform apply

2. Start API
cd api
pip install -r requirements.txt
python app.py

3. Start Dashboard
cd dashboard
npm install
npm start

## Author

Anvesh Reddy - AWS DevOps Engineer
AWS Certified Solutions Architect (SAA-C03)
4 Years Experience | Oregon Systems
Clients: Citi Bank, Flipkart
