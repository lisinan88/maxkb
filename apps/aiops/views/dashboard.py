from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Avg
from datetime import datetime, timedelta
from ..models import SystemMetric, Alert, Incident, AutomationExecution


def aiops_dashboard(request):
    """Main AIOps dashboard view"""
    context = {
        'active_alerts': Alert.objects.filter(status='open').count(),
        'open_incidents': Incident.objects.filter(status__in=['new', 'investigating']).count(),
        'automation_runs': AutomationExecution.objects.filter(
            started_at__gte=datetime.now() - timedelta(days=1)
        ).count(),
    }
    return render(request, 'aiops/dashboard.html', context)


def metrics_api(request):
    """API endpoint for metrics data"""
    hostname = request.GET.get('hostname', 'localhost')
    hours = int(request.GET.get('hours', 24))
    
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    
    metrics = SystemMetric.objects.filter(
        hostname=hostname,
        timestamp__gte=start_time
    ).values('metric_type', 'timestamp', 'value')
    
    # Group by metric type
    data = {}
    for metric in metrics:
        metric_type = metric['metric_type']
        if metric_type not in data:
            data[metric_type] = []
        data[metric_type].append({
            'timestamp': metric['timestamp'].isoformat(),
            'value': metric['value']
        })
    
    return JsonResponse(data)


def alerts_api(request):
    """API endpoint for alerts data"""
    alerts = Alert.objects.filter(status='open').values(
        'id', 'title', 'severity', 'hostname', 'created_at'
    )
    return JsonResponse(list(alerts), safe=False)


def incidents_api(request):
    """API endpoint for incidents data"""
    incidents = Incident.objects.all().values(
        'id', 'title', 'priority', 'status', 'created_at'
    )
    return JsonResponse(list(incidents), safe=False)