"""
CloudWatch Metrics Publisher

Publishes application metrics to AWS CloudWatch for monitoring and alerting.
"""
import boto3
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CloudWatchPublisher:
    """Publishes metrics to AWS CloudWatch"""
    
    def __init__(self, namespace: str = "MLOps/ModelAPI", region: str = "us-east-1"):
        """
        Initialize CloudWatch client
        
        Args:
            namespace: CloudWatch namespace for metrics
            region: AWS region
        """
        self.namespace = namespace
        try:
            self.client = boto3.client('cloudwatch', region_name=region)
            logger.info(f"CloudWatch publisher initialized for namespace: {namespace}")
        except Exception as e:
            logger.warning(f"Failed to initialize CloudWatch client: {e}")
            self.client = None
    
    def publish_metrics(self, metrics: Dict[str, Any]) -> bool:
        """
        Publish application metrics to CloudWatch
        
        Args:
            metrics: Dictionary containing API and model metrics
            
        Returns:
            True if published successfully, False otherwise
        """
        if not self.client:
            return False
        
        try:
            metric_data = []
            
            # API metrics
            api_metrics = metrics.get("api_metrics", {})
            if api_metrics:
                metric_data.extend([
                    {
                        'MetricName': 'TotalRequests',
                        'Value': api_metrics.get('total_requests', 0),
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow()
                    },
                    {
                        'MetricName': 'TotalPredictions',
                        'Value': api_metrics.get('total_predictions', 0),
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow()
                    },
                    {
                        'MetricName': 'Errors',
                        'Value': api_metrics.get('errors', 0),
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow()
                    },
                    {
                        'MetricName': 'AverageResponseTime',
                        'Value': api_metrics.get('average_response_time', 0),
                        'Unit': 'Milliseconds',
                        'Timestamp': datetime.utcnow()
                    }
                ])
            
            # Model metrics
            model_metrics = metrics.get("model_metrics", {})
            if model_metrics:
                metric_data.append({
                    'MetricName': 'ModelLoaded',
                    'Value': 1 if model_metrics.get('model_loaded') else 0,
                    'Unit': 'None',
                    'Timestamp': datetime.utcnow()
                })
            
            # Publish to CloudWatch
            if metric_data:
                self.client.put_metric_data(
                    Namespace=self.namespace,
                    MetricData=metric_data
                )
                logger.debug(f"Published {len(metric_data)} metrics to CloudWatch")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to publish metrics to CloudWatch: {e}")
            return False


# Global instance
cloudwatch_publisher = CloudWatchPublisher()
