# AWS Billing and Cost Management Documentation

## Overview
This document tracks all steps and settings related to AWS billing, cost management, and staying within the Free Tier for your MLOps project.

## Steps Taken

1. **Enabled My Zero-Spend Budget**
   - AWS Budgets is set to alert if any spend occurs (zero-spend budget).
   - Budget health and alerts reset after each budget period.
   - Budget information updates up to three times a day (with 8-12 hour delay).
   - There may be a delay between incurring a charge and receiving a notification.

2. **Enabled Free Tier Usage Alerts** (must be activated separately from your zero-spend budget)
   - Notifies you when you're approaching or exceeding Free Tier limits for specific services.
   - To activate: 
     - Open the AWS Billing and Cost Management console
     - In the navigation pane, choose "Billing preferences"
     - In the "Alert preferences" section, choose "Edit"
     - Select "Receive AWS Free Tier usage alerts"
     - Optionally, add additional email addresses to receive alerts
     - Choose "Update" to save your changes

3. **Set Up Cost Explorer**
   - Activated Cost Explorer for visualizing and analyzing spending trends.

4. **Reviewed Billing Dashboard**
   - Regularly check the Billing dashboard for up-to-date cost and usage information.

5. **(Optional) Set Up CloudWatch Alarms**
   - For monitoring specific resource usage (e.g., S3, Lambda, EC2) if needed.

## Recommendations
- Enable both zero-spend budget and Free Tier usage alerts for comprehensive coverage.
- The zero-spend budget notifies you about any charges, while Free Tier alerts warn you about service-specific Free Tier usage.
- Regularly check your usage in the AWS Billing and Cost Management console for detailed insights per service, region, and type.
- Be aware of the delay in budget notifications and actual charges.
- Keep all billing-related alerts enabled to avoid unexpected costs.
- Document any changes to billing settings or new budgets here.

## Sources
- Building a three-tier architecture on a budget | AWS Architecture Blog
- How do I set up billing alerts in AWS to notify me if I go over my free tier? | AWS re:Post
- Tracking your AWS Free Tier usage - AWS Billing

---

_Last updated: June 21, 2025_
