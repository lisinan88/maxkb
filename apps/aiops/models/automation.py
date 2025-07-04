from django.db import models
from django.contrib.auth.models import User


class AutomationRule(models.Model):
    TRIGGER_TYPES = [
        ('metric_threshold', 'Metric Threshold'),
        ('alert_created', 'Alert Created'),
        ('incident_created', 'Incident Created'),
        ('schedule', 'Scheduled'),
    ]
    
    ACTION_TYPES = [
        ('restart_service', 'Restart Service'),
        ('scale_resources', 'Scale Resources'),
        ('send_notification', 'Send Notification'),
        ('run_script', 'Run Script'),
        ('create_ticket', 'Create Ticket'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_TYPES)
    trigger_conditions = models.JSONField(default=dict)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    action_config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'aiops_automation_rule'


class AutomationExecution(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    rule = models.ForeignKey(AutomationRule, on_delete=models.CASCADE, related_name='executions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    trigger_data = models.JSONField(default=dict)
    result = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'aiops_automation_execution'