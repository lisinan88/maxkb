import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from django.db.models import Q
from datetime import datetime, timedelta
from ..models import SystemMetric, Alert


class AnomalyDetector:
    def __init__(self, contamination=0.1):
        self.contamination = contamination
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.scaler = StandardScaler()
        
    def prepare_data(self, hostname, hours_back=24):
        """Prepare metric data for anomaly detection"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        metrics = SystemMetric.objects.filter(
            hostname=hostname,
            timestamp__gte=start_time,
            metric_type__in=['cpu', 'memory', 'disk']
        ).order_by('timestamp')
        
        if not metrics.exists():
            return None, None
            
        # Pivot data by metric type
        data = {}
        for metric in metrics:
            if metric.metric_type not in data:
                data[metric.metric_type] = []
            data[metric.metric_type].append(metric.value)
        
        # Ensure all metric types have same length
        min_length = min(len(values) for values in data.values())
        features = []
        for i in range(min_length):
            row = [data[metric_type][i] for metric_type in ['cpu', 'memory', 'disk']]
            features.append(row)
            
        return np.array(features), list(metrics)[:min_length]
    
    def detect_anomalies(self, hostname):
        """Detect anomalies in system metrics"""
        features, metrics = self.prepare_data(hostname)
        
        if features is None:
            return []
            
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Detect anomalies
        anomaly_scores = self.model.fit_predict(features_scaled)
        anomaly_indices = np.where(anomaly_scores == -1)[0]
        
        anomalies = []
        for idx in anomaly_indices:
            if idx < len(metrics):
                anomalies.append(metrics[idx])
                
        return anomalies
    
    def create_anomaly_alerts(self, anomalies):
        """Create alerts for detected anomalies"""
        for metric in anomalies:
            Alert.objects.create(
                title=f'Anomaly Detected: {metric.metric_type.upper()}',
                description=f'Anomalous {metric.metric_type} value {metric.value}% detected on {metric.hostname}',
                severity='medium',
                hostname=metric.hostname,
                metric_type=metric.metric_type,
                threshold_value=0,  # No specific threshold for anomalies
                current_value=metric.value
            )
    
    def run_detection(self, hostname):
        """Run anomaly detection for a hostname"""
        anomalies = self.detect_anomalies(hostname)
        if anomalies:
            self.create_anomaly_alerts(anomalies)
        return len(anomalies)