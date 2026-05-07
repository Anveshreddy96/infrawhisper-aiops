import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.incidents import router as incidents_router

# Create the FastAPI app
# title and description show up in the auto-generated docs page
app = FastAPI(
    title       = "InfraWhisper AIOps API",
    description = "AI-powered incident triage using AWS Bedrock + Claude Sonnet 4.6",
    version     = "1.0.0"
)

# CORS middleware — allows the React dashboard to call this API
# Without this, browsers block API calls from different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],  # allow all origins (ok for portfolio project)
    allow_credentials = True,
    allow_methods     = ["*"],  # allow GET, POST, PUT, DELETE etc
    allow_headers     = ["*"],  # allow all headers
)

# Register our incidents router
# prefix="/api/v1" means all routes become /api/v1/incidents etc
app.include_router(incidents_router, prefix="/api/v1")

# Root endpoint — shows when someone visits http://your-ip:8000/
@app.get("/")
def root():
    return {
        "service"     : "InfraWhisper AIOps Platform",
        "version"     : "1.0.0",
        "description" : "AI-powered incident triage using AWS Bedrock + Claude Sonnet 4.6",
        "docs"        : "/docs",
        "endpoints"   : {
            "health"           : "/api/v1/health",
            "list_incidents"   : "/api/v1/incidents",
            "get_incident"     : "/api/v1/incidents/{incident_id}",
            "simulate_alarm"   : "/api/v1/incidents/simulate"
        }
    }

# This block runs when you start the file directly
# uvicorn is the server, host 0.0.0.0 means accept from any IP
# port 8000 is the port we opened in security group earlier
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host     = "0.0.0.0",
        port     = 8000,
        reload   = True   # auto-restart when code changes
    )
