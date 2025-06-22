# AWS Resource Cleanup and Cost Minimization

## Why Resource Cleanup Matters
To minimize AWS costs and avoid unexpected charges, it’s important to regularly check for and terminate any active services and resources you no longer need. AWS bills for all active resources, even if you’re not using them.

## How to Identify and Clean Up Resources

1. **Check Active Services and Regions**
   - Go to the [AWS Billing and Cost Management console](https://console.aws.amazon.com/billing/).
   - Review the "Bills" and "Cost Explorer" sections to see which services and regions are incurring charges.
   - Use the "Resource Explorer" or service-specific dashboards (e.g., EC2, S3, Lambda) to list active resources.

2. **Terminate or Delete Unused Resources**
   - For each service, navigate to its dashboard and review running or allocated resources (instances, buckets, functions, etc.).
   - Terminate, stop, or delete any resources you no longer need.
   - Double-check all regions, as resources in non-default regions can also incur charges.

3. **Automate Cleanup (Optional)**
   - Use AWS Budgets, Lambda, or third-party tools to automate resource cleanup or receive alerts for idle resources.

## Best Practices
- Regularly review your AWS account for unused resources.
- Always check all regions, not just your default region.
- Document any cleanup actions taken for future reference.

---

_Last updated: June 21, 2025_
