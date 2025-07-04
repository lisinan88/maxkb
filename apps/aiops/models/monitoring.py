from django.db import models
from django.contrib.auth.models import User
import json


class SystemMetric(models.Model):
    METRIC_TYPES = [
        ('cpu', 'CPU Usage'),
        ('memory', 'Memory Usage'),
        ('disk', 'Disk Usage'),
        ('network', 'Network Traffic'),
        ('response_time', 'Response Time'),
        ('error_rate', 'Error Rate'),
        ('throughput', 'Throughput'),
    ]
    
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    hostname = models.CharField(max_length=255)
    value = models.FloatField()
    unit = models.CharField(max_length=20, default='%')
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'aiops_system_metric'
        indexes = [
            models.Index(fields=['metric_type', 'hostname', 'timestamp']),
        ]


class Alert(models.Model):
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    hostname = models.CharField(max_length=255)
    metric_type = models.CharField(max_length=50)
    threshold_value = models.FloatField()
    current_value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'aiops_alert'