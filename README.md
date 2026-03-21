# GraphSent — AI-Powered Fund Flow Tracking

GraphSent is an AI-powered Fund Flow Tracking and Fraud Detection system for banking. Built for the PSBs Hackathon Series 2026.

## Architecture

```text
    [ React Frontend (Dashboard & GraphView) ]
                  |
             (REST APIs)
                  |
           [ FastAPI Backend ]
                  |
  ------------------------------------
  |       |       |       |          |
IForest Config  Graph Profile   Risk Engine
                  |
               [ Neo4j ]
```

## Quick Start
1. Ensure Docker and Docker Compose are installed.
2. Run:
   ```bash
   docker-compose up --build
   ```
3. Open http://localhost:3000

## How to Demo Circular Fraud
- Wait for the initial detection pipeline to run on backend startup.
- The top alerts will be listed as CRITICAL. Click on any of the top circular fraud ones.
- The visual graph will show the 4-hop chain.
- Click "Download STR (PDF)" to see the auto-generated regulatory report.
