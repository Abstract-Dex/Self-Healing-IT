# Self Healing IT Infra

This repository contains an approach to automate the process of identifying and resolving IT issues using state-of-the-art techniques such as RAG and Agentic systems. The goal is to create a self-healing IT system that can proactively detect and fix problems without human intervention.

**Architecture Overview:**

1. Every IT issue is logged as a ticket in the ticket database.
2. The ticket database is used to identify similar past issues that have been resolved either by the IT team or the agent itself.
3. If similar past issues are found, then the agent uses the information to generate a troubleshooting guide.
4. If no similar past issues are found, then the agent uses the web search to find the information related to the current issue.
5. For either case, the agent generates a troubleshooting guide that can be used to resolve the issue.

## Workflow Diagram

<img width="673" height="1235" alt="Self-healing-it" src="https://github.com/user-attachments/assets/39480eb2-3c30-4a83-af42-bae4a5221b08" />

**NOTE:** This project is a work in progress and is not yet ready for production.
