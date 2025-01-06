"""Performance monitoring and metrics system."""

from typing import Optional, Dict, Any, List
import time
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import psutil
import threading
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    start_http_server
)
from utils.logger import log

@dataclass
class ServiceMetrics:
    """Service-level metrics."""
    requests: int = 0
    errors: int = 0
    total_duration: float = 0.0
    avg_duration: float = 0.0
    success_rate: float = 0.0
    last_request: Optional[datetime] = None
    
@dataclass
class ResourceMetrics:
    """System resource metrics."""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_usage_percent: float = 0.0
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0
    
class MetricsService:
    """Service for collecting and reporting metrics."""
    
    def __init__(
        self,
        metrics_dir: str = "metrics",
        export_interval: int = 60,
        enable_prometheus: bool = True,
        prometheus_port: int = 8000
    ):
        """Initialize metrics service.
        
        Args:
            metrics_dir: Directory for metrics storage
            export_interval: Metrics export interval in seconds
            enable_prometheus: Whether to enable Prometheus metrics
            prometheus_port: Prometheus metrics port
        """
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        self.export_interval = export_interval
        self.enable_prometheus = enable_prometheus
        
        # Initialize service metrics
        self.services: Dict[str, ServiceMetrics] = {
            "riddle": ServiceMetrics(),
            "video": ServiceMetrics(),
            "audio": ServiceMetrics()
        }
        
        # Initialize resource metrics
        self.resources = ResourceMetrics()
        
        # Initialize Prometheus metrics
        if enable_prometheus:
            self._init_prometheus(prometheus_port)
            
        # Start metrics collection
        self._start_collection()
        
    def _init_prometheus(self, port: int) -> None:
        """Initialize Prometheus metrics.
        
        Args:
            port: Prometheus metrics port
        """
        # Service metrics
        self.prom_requests = Counter(
            "riddler_requests_total",
            "Total number of requests",
            ["service"]
        )
        
        self.prom_errors = Counter(
            "riddler_errors_total",
            "Total number of errors",
            ["service"]
        )
        
        self.prom_duration = Histogram(
            "riddler_request_duration_seconds",
            "Request duration in seconds",
            ["service"]
        )
        
        self.prom_success_rate = Gauge(
            "riddler_success_rate",
            "Request success rate",
            ["service"]
        )
        
        # Resource metrics
        self.prom_cpu = Gauge(
            "riddler_cpu_percent",
            "CPU usage percentage"
        )
        
        self.prom_memory = Gauge(
            "riddler_memory_percent",
            "Memory usage percentage"
        )
        
        self.prom_disk = Gauge(
            "riddler_disk_percent",
            "Disk usage percentage"
        )
        
        self.prom_network_sent = Counter(
            "riddler_network_bytes_sent",
            "Network bytes sent"
        )
        
        self.prom_network_recv = Counter(
            "riddler_network_bytes_recv",
            "Network bytes received"
        )
        
        # Start Prometheus server
        start_http_server(port)
        
    def _start_collection(self) -> None:
        """Start metrics collection thread."""
        def collect_metrics():
            while True:
                try:
                    # Collect resource metrics
                    self.resources.cpu_percent = psutil.cpu_percent()
                    self.resources.memory_percent = psutil.virtual_memory().percent
                    self.resources.disk_usage_percent = psutil.disk_usage("/").percent
                    
                    net_io = psutil.net_io_counters()
                    self.resources.network_bytes_sent = net_io.bytes_sent
                    self.resources.network_bytes_recv = net_io.bytes_recv
                    
                    # Update Prometheus metrics
                    if self.enable_prometheus:
                        self.prom_cpu.set(self.resources.cpu_percent)
                        self.prom_memory.set(self.resources.memory_percent)
                        self.prom_disk.set(self.resources.disk_usage_percent)
                        self.prom_network_sent.inc(self.resources.network_bytes_sent)
                        self.prom_network_recv.inc(self.resources.network_bytes_recv)
                        
                    # Export metrics
                    self.export_metrics()
                    
                except Exception as e:
                    log.error(f"Failed to collect metrics: {e}")
                    
                time.sleep(self.export_interval)
                
        # Start collection thread
        thread = threading.Thread(
            target=collect_metrics,
            daemon=True
        )
        thread.start()
        
    def record_request(
        self,
        service: str,
        duration: float,
        success: bool = True
    ) -> None:
        """Record a service request.
        
        Args:
            service: Service name
            duration: Request duration in seconds
            success: Whether request was successful
        """
        if service not in self.services:
            self.services[service] = ServiceMetrics()
            
        metrics = self.services[service]
        metrics.requests += 1
        metrics.total_duration += duration
        metrics.avg_duration = metrics.total_duration / metrics.requests
        metrics.last_request = datetime.now()
        
        if not success:
            metrics.errors += 1
            
        metrics.success_rate = (
            (metrics.requests - metrics.errors) / metrics.requests
            if metrics.requests > 0
            else 0.0
        )
        
        # Update Prometheus metrics
        if self.enable_prometheus:
            self.prom_requests.labels(service=service).inc()
            if not success:
                self.prom_errors.labels(service=service).inc()
            self.prom_duration.labels(service=service).observe(duration)
            self.prom_success_rate.labels(service=service).set(metrics.success_rate)
            
    def export_metrics(self) -> None:
        """Export metrics to disk."""
        try:
            # Prepare metrics data
            data = {
                "timestamp": datetime.now().isoformat(),
                "services": {
                    name: asdict(metrics)
                    for name, metrics in self.services.items()
                },
                "resources": asdict(self.resources)
            }
            
            # Write to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            metrics_file = self.metrics_dir / f"metrics_{timestamp}.json"
            
            with open(metrics_file, "w") as f:
                json.dump(data, f, indent=2)
                
            # Cleanup old files
            self._cleanup_old_metrics()
            
        except Exception as e:
            log.error(f"Failed to export metrics: {e}")
            
    def _cleanup_old_metrics(self, max_age_days: int = 7) -> None:
        """Clean up old metrics files.
        
        Args:
            max_age_days: Maximum age of metrics files in days
        """
        try:
            now = datetime.now()
            max_age = timedelta(days=max_age_days)
            
            for file in self.metrics_dir.glob("metrics_*.json"):
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                if now - mtime > max_age:
                    file.unlink()
                    
        except Exception as e:
            log.error(f"Failed to cleanup metrics: {e}")
            
    def get_service_stats(
        self,
        service: str,
        time_range: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Get service statistics.
        
        Args:
            service: Service name
            time_range: Optional time range to filter metrics
            
        Returns:
            Service statistics
        """
        if service not in self.services:
            return {}
            
        metrics = self.services[service]
        stats = asdict(metrics)
        
        if time_range and metrics.last_request:
            # Filter metrics by time range
            start_time = datetime.now() - time_range
            
            # Load historical data
            filtered_metrics = []
            for file in sorted(self.metrics_dir.glob("metrics_*.json")):
                try:
                    data = json.loads(file.read_text())
                    timestamp = datetime.fromisoformat(data["timestamp"])
                    
                    if timestamp >= start_time:
                        service_data = data["services"].get(service, {})
                        filtered_metrics.append(service_data)
                        
                except Exception:
                    continue
                    
            if filtered_metrics:
                # Calculate aggregated stats
                total_requests = sum(m["requests"] for m in filtered_metrics)
                total_errors = sum(m["errors"] for m in filtered_metrics)
                total_duration = sum(m["total_duration"] for m in filtered_metrics)
                
                stats.update({
                    "requests_in_range": total_requests,
                    "errors_in_range": total_errors,
                    "avg_duration_in_range": (
                        total_duration / total_requests
                        if total_requests > 0
                        else 0.0
                    ),
                    "success_rate_in_range": (
                        (total_requests - total_errors) / total_requests
                        if total_requests > 0
                        else 0.0
                    )
                })
                
        return stats
        
    def get_resource_stats(
        self,
        time_range: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Get resource statistics.
        
        Args:
            time_range: Optional time range to filter metrics
            
        Returns:
            Resource statistics
        """
        stats = asdict(self.resources)
        
        if time_range:
            # Load historical data
            start_time = datetime.now() - time_range
            resource_metrics = []
            
            for file in sorted(self.metrics_dir.glob("metrics_*.json")):
                try:
                    data = json.loads(file.read_text())
                    timestamp = datetime.fromisoformat(data["timestamp"])
                    
                    if timestamp >= start_time:
                        resource_metrics.append(data["resources"])
                        
                except Exception:
                    continue
                    
            if resource_metrics:
                # Calculate aggregated stats
                stats.update({
                    "avg_cpu_percent": sum(
                        m["cpu_percent"] for m in resource_metrics
                    ) / len(resource_metrics),
                    "avg_memory_percent": sum(
                        m["memory_percent"] for m in resource_metrics
                    ) / len(resource_metrics),
                    "avg_disk_usage_percent": sum(
                        m["disk_usage_percent"] for m in resource_metrics
                    ) / len(resource_metrics),
                    "total_network_bytes_sent": sum(
                        m["network_bytes_sent"] for m in resource_metrics
                    ),
                    "total_network_bytes_recv": sum(
                        m["network_bytes_recv"] for m in resource_metrics
                    )
                })
                
        return stats

# Initialize global metrics service
metrics = MetricsService() 