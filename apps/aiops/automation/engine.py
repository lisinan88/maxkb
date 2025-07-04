import subprocess
import json
from datetime import datetime
from django.utils import timezone
from ..models import AutomationRule, AutomationExecution, Alert, Incident


class AutomationEngine:
    def __init__(self):
        self.action_handlers = {
            'restart_service': self.restart_service,
            'scale_resources': self.scale_resources,
            'send_notification': self.send_notification,
            'run_script': self.run_script,
            'create_ticket': self.create_ticket,
        }
    
    def process_triggers(self):
        """Process all active automation rules"""
        active_rules = AutomationRule.objects.filter(is_active=True)
        
        for rule in active_rules:
            if self.should_trigger(rule):
                self.execute_rule(rule)
    
    def should_trigger(self, rule):
        """Check if rule should be triggered"""
        if rule.trigger_type == 'alert_created':
            # Check for new alerts matching conditions
            conditions = rule.trigger_conditions
            alerts = Alert.objects.filter(
                status='open',
                severity__in=conditions.get('severities', ['high', 'critical'])
            )
            return alerts.exists()
            
        elif rule.trigger_type == 'metric_threshold':
            # Check metric thresholds
            from ..models import SystemMetric
            conditions = rule.trigger_conditions
            recent_metrics = SystemMetric.objects.filter(
                metric_type=conditions.get('metric_type'),
                hostname=conditions.get('hostname'),
                timestamp__gte=timezone.now() - timezone.timedelta(minutes=5)
            ).order_by('-timestamp')[:1]
            
            if recent_metrics:
                return recent_metrics[0].value > conditions.get('threshold', 80)
                
        return False
    
    def execute_rule(self, rule):
        """Execute automation rule"""
        execution = AutomationExecution.objects.create(
            rule=rule,
            status='running',
            trigger_data={}
        )
        
        try:
            handler = self.action_handlers.get(rule.action_type)
            if handler:
                result = handler(rule.action_config)
                execution.status = 'success'
                execution.result = result
            else:
                execution.status = 'failed'
                execution.error_message = f'Unknown action type: {rule.action_type}'
                
        except Exception as e:
            execution.status = 'failed'
            execution.error_message = str(e)
        
        execution.completed_at = timezone.now()
        execution.save()
        
        return execution
    
    def restart_service(self, config):
        """Restart a system service"""
        service_name = config.get('service_name')
        if not service_name:
            raise ValueError('Service name not specified')
            
        try:
            result = subprocess.run(['systemctl', 'restart', service_name], 
                                  capture_output=True, text=True, check=True)
            return {'success': True, 'output': result.stdout}
        except subprocess.CalledProcessError as e:
            raise Exception(f'Failed to restart service: {e.stderr}')
    
    def scale_resources(self, config):
        """Scale system resources (placeholder)"""
        return {'success': True, 'message': 'Resource scaling triggered'}
    
    def send_notification(self, config):
        """Send notification (placeholder)"""
        return {'success': True, 'message': 'Notification sent'}
    
    def run_script(self, config):
        """Run custom script"""
        script_path = config.get('script_path')
        if not script_path:
            raise ValueError('Script path not specified')
            
        try:
            result = subprocess.run([script_path], capture_output=True, text=True, check=True)
            return {'success': True, 'output': result.stdout}
        except subprocess.CalledProcessError as e:
            raise Exception(f'Script execution failed: {e.stderr}')
    
    def create_ticket(self, config):
        """Create incident ticket"""
        title = config.get('title', 'Automated Incident')
        description = config.get('description', 'Automatically created incident')
        
        from django.contrib.auth.models import User
        system_user = User.objects.filter(is_superuser=True).first()
        
        incident = Incident.objects.create(
            title=title,
            description=description,
            priority='medium',
            created_by=system_user
        )
        
        return {'success': True, 'incident_id': incident.id}