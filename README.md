# Kubernetes Auto Remediation using AWS Lambda

## Overview
This project provides an automated remediation solution for common Kubernetes issues using AWS Lambda.
It listens for events related to pod failures and node issues via AWS EventBridge and applies fixes accordingly.

## Issues Fixed:
- **OOMKilled**: Increases memory limits for affected pods.
- **CrashLoopBackOff**: Deletes and restarts failing pods.
- **NodeNotReady**: Uncordons and restarts problematic nodes.

## Deployment Steps:
1. Deploy the AWS Lambda function.
2. Configure AWS EventBridge to trigger Lambda on Kubernetes pod state changes.
3. Assign the necessary IAM permissions to Lambda for interacting with EKS and EC2.

## How It Works:
1. EventBridge captures pod failures.
2. Lambda receives the event and applies the corresponding remediation fix.
3. Notifications can be sent via SNS, Slack, or CloudWatch Logs.

Future Enhancements
1. Make the use cases dynamic and use AIOPS kind of approach for all possible issues
2. Implement notifications via Slack or SNS.
