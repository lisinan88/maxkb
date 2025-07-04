import psutil
import time
import requests
from datetime import datetime
from ..models import SystemMetric, Alert
from django.utils import timezone


class MetricsCollector:
    def __init__(self, hostname='localhost'):
        self.hostname = hostname
        
    def collect_system_metrics(self):
        """Collect basic system metrics"""
        metrics = []
        
        # CPU Usage
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics.append(SystemMetric(
            metric_type='cpu',
            hostname=self.hostname,
            value=cpu_percent,
            unit='%'
        ))
        
        # Memory Usage
        memory = psutil.virtual_memory()
        metrics.append(SystemMetric(
            metric_type='memory',
            hostname=self.hostname,
            value=memory.percent,
            unit='%'
        ))
        
        # Disk Usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        metrics.append(SystemMetric(
            metric_type='disk',
            hostname=self.hostname,
            value=disk_percent,
            unit='%'
        ))
        
        # Network I/O
        network = psutil.net_io_counters()
        metrics.append(SystemMetric(
            metric_type='network',
            hostname=self.hostname,
            value=network.bytes_sent + network.bytes_recv,
            unit='bytes',
            metadata={'bytes_sent': network.bytes_sent, 'bytes_recv': network.bytes_recv}
        ))
        
        return metrics
    
    def check_thresholds(self, metrics):
        """Check metrics against thresholds and create alerts"""
        thresholds = {
            'cpu': 80,
            'memory': 85,
            'disk': 90,
        }
        
        for metric in metrics:
            if metric.metric_type in thresholds:
                threshold = thresholds[metric.metric_type]
                if metric.value > threshold:
                    self.create_alert(metric, threshold)
    
    def create_alert(self, metric, threshold):
        """Create alert for threshold breach"""
        severity = 'high' if metric.value > threshold * 1.2 else 'medium'
        
        Alert.objects.create(
            title=f'{metric.metric_type.upper()} Usage Alert',
            description=f'{metric.metric_type.upper()} usage is {metric.value}% on {metric.hostname}',
            severity=severity,
            hostname=metric.hostname,
            metric_type=metric.metric_type,
            threshold_value=threshold,
            current_value=metric.value
        )
    
    def run_collection(self):
        """Run metrics collection cycle"""
        metrics = self.collect_system_metrics()
        SystemMetric.objects.bulk_create(metrics)
        self.check_thresholds(metrics)
        return len(metrics)