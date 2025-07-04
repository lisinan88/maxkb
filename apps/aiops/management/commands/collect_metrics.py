from django.core.management.base import BaseCommand
from ...monitoring.metrics_collector import MetricsCollector
from ...anomaly.detector import AnomalyDetector
from ...automation.engine import AutomationEngine


class Command(BaseCommand):
    help = 'Collect system metrics and run AIOps analysis'

    def add_arguments(self, parser):
        parser.add_argument('--hostname', type=str, default='localhost')
        parser.add_argument('--anomaly-detection', action='store_true')
        parser.add_argument('--automation', action='store_true')

    def handle(self, *args, **options):
        hostname = options['hostname']
        
        # Collect metrics
        collector = MetricsCollector(hostname)
        metrics_count = collector.run_collection()
        self.stdout.write(f'Collected {metrics_count} metrics for {hostname}')
        
        # Run anomaly detection
        if options['anomaly_detection']:
            detector = AnomalyDetector()
            anomalies = detector.run_detection(hostname)
            self.stdout.write(f'Detected {anomalies} anomalies')
        
        # Process automation rules
        if options['automation']:
            engine = AutomationEngine()
            engine.process_triggers()
            self.stdout.write('Processed automation triggers')