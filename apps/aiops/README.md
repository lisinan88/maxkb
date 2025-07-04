# AIOps Module for MaxKB

This module transforms MaxKB into a comprehensive AIOps (Artificial Intelligence for IT Operations) platform.

## Features

### 1. System Monitoring
- Real-time collection of system metrics (CPU, Memory, Disk, Network)
- Configurable thresholds and alerting
- Historical data storage and analysis

### 2. Anomaly Detection
- Machine learning-based anomaly detection using Isolation Forest
- Automatic detection of unusual system behavior
- Proactive alerting for potential issues

### 3. Incident Management
- Incident tracking and lifecycle management
- Priority-based incident handling
- Incident logs and resolution tracking

### 4. Automation Engine
- Rule-based automation for common remediation tasks
- Support for service restarts, resource scaling, notifications
- Custom script execution capabilities

### 5. Performance Analytics
- System health scoring
- Trend analysis for metrics
- Alert statistics and reporting

## Usage

### Collect Metrics
```bash
python manage.py collect_metrics --hostname localhost --anomaly-detection --automation
```

### Access Dashboard
Navigate to `/aiops/` to view the AIOps dashboard with real-time metrics and alerts.

### API Endpoints
- `/aiops/api/metrics/` - Get metrics data
- `/aiops/api/alerts/` - Get active alerts
- `/aiops/api/incidents/` - Get incident data

## Configuration

The AIOps module integrates seamlessly with MaxKB's existing configuration system and uses the same database and authentication mechanisms.

## Models

- **SystemMetric**: Stores system performance metrics
- **Alert**: Manages alerts and notifications
- **Incident**: Tracks incidents and their resolution
- **AutomationRule**: Defines automation rules and triggers
- **AutomationExecution**: Logs automation executions

## Installation

1. Install additional dependencies:
```bash
pip install -r requirements-aiops.txt
```

2. Run database migrations:
```bash
python manage.py migrate
```

3. Start collecting metrics:
```bash
python manage.py collect_metrics
```