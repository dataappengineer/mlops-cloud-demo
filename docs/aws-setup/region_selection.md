# AWS Region Selection Guide

AWS root and IAM users are global, but resources (S3, EC2, Lambda, etc.) are created in specific regions.

## Recommended Regions for Colombia
- **us-east-1 (N. Virginia, USA):** Closest, most popular, best supported, and often the default.
- **us-east-2 (Ohio, USA):** Good alternative.
- **us-west-2 (Oregon, USA):** Another option.

**Recommendation:**
Choose `us-east-1` (N. Virginia) unless you have a specific reason to use another region. It’s closest to Colombia, has the most services, and is often the cheapest.

You can always change the region for each service or project as needed.
