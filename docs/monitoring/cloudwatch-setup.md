# CloudWatch Monitoring Setup

## Overview

The Model API publishes custom metrics to AWS CloudWatch for monitoring and alerting. Metrics are automatically published every time the `/metrics` endpoint is called.

## Metrics Published

### API Metrics
- **TotalRequests**: Cumulative count of all API requests
- **TotalPredictions**: Count of successful predictions
- **Errors**: Count of API errors
- **AverageResponseTime**: Mean response time in milliseconds

### Model Metrics
- **ModelLoaded**: Binary indicator (1=loaded, 0=not loaded)

## CloudWatch Dashboard

Create a dashboard in AWS Console:

```bash
# Create dashboard from JSON configuration
aws cloudwatch put-dashboard \
  --dashboard-name MLOps-Model-API \
  --dashboard-body file://infrastructure/cloudwatch-dashboard.json \
  --region us-east-1 \
  --profile mlops-admin
```

Or manually create via AWS Console:
1. Go to CloudWatch → Dashboards → Create dashboard
2. Add widgets for each metric in namespace `MLOps/ModelAPI`
3. Add log insights widget for error logs

## Viewing Metrics

### AWS Console
Navigate to: **CloudWatch → Metrics → MLOps/ModelAPI**

### CLI
```bash
# Get recent request count
aws cloudwatch get-metric-statistics \
  --namespace MLOps/ModelAPI \
  --metric-name TotalRequests \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum \
  --region us-east-1

# Get error rate
aws cloudwatch get-metric-statistics \
  --namespace MLOps/ModelAPI \
  --metric-name Errors \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum \
  --region us-east-1
```

### API Endpoint
```bash
# Local metrics endpoint
curl http://mlops-demo-dev-alb-1849542828.us-east-1.elb.amazonaws.com/metrics | jq .
```

## Setting Up Alarms

### High Error Rate Alarm
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name model-api-high-error-rate \
  --alarm-description "Alert when error rate exceeds 5 per minute" \
  --namespace MLOps/ModelAPI \
  --metric-name Errors \
  --statistic Sum \
  --period 60 \
  --evaluation-periods 2 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --region us-east-1 \
  --profile mlops-admin
```

### High Latency Alarm
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name model-api-high-latency \
  --alarm-description "Alert when response time exceeds 500ms" \
  --namespace MLOps/ModelAPI \
  --metric-name AverageResponseTime \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 500 \
  --comparison-operator GreaterThanThreshold \
  --region us-east-1 \
  --profile mlops-admin
```

### Model Not Loaded Alarm
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name model-api-model-not-loaded \
  --alarm-description "Alert when model fails to load" \
  --namespace MLOps/ModelAPI \
  --metric-name ModelLoaded \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 0.5 \
  --comparison-operator LessThanThreshold \
  --region us-east-1 \
  --profile mlops-admin
```

## Log Insights Queries

### Recent Errors
```sql
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 20
```

### Slow Requests (>100ms)
```sql
fields @timestamp, @message
| filter @message like /processing_time_ms/
| parse @message /processing_time_ms: (?<latency>\d+\.\d+)/
| filter latency > 100
| sort @timestamp desc
```

### Prediction Volume by Hour
```sql
fields @timestamp
| filter @message like /Prediction completed/
| stats count() by bin(5m)
```

## Cost Considerations

- **Custom Metrics**: First 10,000 metrics free per month, then $0.30 per metric
- **CloudWatch Logs**: $0.50/GB ingested, $0.03/GB stored
- **Dashboard**: $3.00/month per dashboard

Current setup publishes ~5 metrics every time `/metrics` is called, well within free tier for typical usage.

## Monitoring Best Practices

1. **Set up alarms** for critical metrics (errors, latency, model health)
2. **Review dashboards daily** during first week of deployment
3. **Create SNS topics** for alarm notifications
4. **Use log insights** to troubleshoot issues
5. **Monitor costs** in AWS Billing console

## Related Documentation
- [AWS CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
- [ECS Container Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ContainerInsights.html)
- [API Metrics Endpoint](../model-api/app/main.py#L132)
