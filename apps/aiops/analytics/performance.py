import pandas as pd
from datetime import datetime, timedelta
from django.db.models import Avg, Max, Min
from ..models import SystemMetric, Alert, Incident


class PerformanceAnalyzer:
    def __init__(self):
        pass
    
    def get_system_health_score(self, hostname, hours=24):
        """Calculate overall system health score"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # Get average metrics
        metrics = SystemMetric.objects.filter(
            hostname=hostname,
            timestamp__gte=start_time
        ).values('metric_type').annotate(
            avg_value=Avg('value'),
            max_value=Max('value')
        )
        
        scores = {}
        for metric in metrics:
            metric_type = metric['metric_type']
            avg_val = metric['avg_value']
            max_val = metric['max_value']
            
            if metric_type in ['cpu', 'memory', 'disk']:
                # Lower is better for resource usage
                score = max(0, 100 - avg_val)
                scores[metric_type] = score
        
        # Calculate overall score
        if scores:
            overall_score = sum(scores.values()) / len(scores)
        else:
            overall_score = 0
            
        return {
            'overall_score': round(overall_score, 2),
            'metric_scores': scores,
            'grade': self._get_grade(overall_score)
        }
    
    def _get_grade(self, score):
        """Convert score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def get_trend_analysis(self, hostname, metric_type, days=7):
        """Analyze metric trends"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        metrics = SystemMetric.objects.filter(
            hostname=hostname,
            metric_type=metric_type,
            timestamp__gte=start_time
        ).order_by('timestamp')
        
        if not metrics.exists():
            return None
            
        values = [m.value for m in metrics]
        timestamps = [m.timestamp for m in metrics]
        
        # Simple trend calculation
        if len(values) > 1:
            trend = (values[-1] - values[0]) / len(values)
        else:
            trend = 0
            
        return {
            'metric_type': metric_type,
            'trend': 'increasing' if trend > 1 else 'decreasing' if trend < -1 else 'stable',
            'trend_value': round(trend, 2),
            'current_value': values[-1] if values else 0,
            'avg_value': sum(values) / len(values) if values else 0,
            'max_value': max(values) if values else 0,
            'min_value': min(values) if values else 0
        }
    
    def get_alert_statistics(self, days=30):
        """Get alert statistics"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        alerts = Alert.objects.filter(created_at__gte=start_time)
        
        stats = {
            'total_alerts': alerts.count(),
            'by_severity': {},
            'by_status': {},
            'by_metric_type': {},
            'resolution_time_avg': 0
        }
        
        # Group by severity
        for severity in ['low', 'medium', 'high', 'critical']:
            stats['by_severity'][severity] = alerts.filter(severity=severity).count()
        
        # Group by status
        for status in ['open', 'acknowledged', 'resolved', 'closed']:
            stats['by_status'][status] = alerts.filter(status=status).count()
        
        # Group by metric type
        metric_types = alerts.values_list('metric_type', flat=True).distinct()
        for metric_type in metric_types:
            stats['by_metric_type'][metric_type] = alerts.filter(metric_type=metric_type).count()
        
        # Calculate average resolution time
        resolved_alerts = alerts.filter(resolved_at__isnull=False)
        if resolved_alerts.exists():
            total_resolution_time = sum([
                (alert.resolved_at - alert.created_at).total_seconds()
                for alert in resolved_alerts
            ])
            stats['resolution_time_avg'] = total_resolution_time / resolved_alerts.count() / 3600  # in hours
        
        return stats