"""Application metrics and monitoring."""
import time
import threading
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class MetricPoint:
    """Single metric data point."""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """Collects and manages application metrics."""
    
    def __init__(self, max_points: int = 1000):
        self.max_points = max_points
        self._metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._lock = threading.Lock()
    
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        with self._lock:
            key = self._make_key(name, tags)
            self._counters[key] += value
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric value."""
        with self._lock:
            key = self._make_key(name, tags)
            self._gauges[key] = value
    
    def record_timing(self, name: str, duration: float, tags: Optional[Dict[str, str]] = None):
        """Record a timing metric."""
        with self._lock:
            key = self._make_key(name, tags)
            point = MetricPoint(timestamp=datetime.utcnow(), value=duration, tags=tags or {})
            self._metrics[key].append(point)
    
    def get_counter(self, name: str, tags: Optional[Dict[str, str]] = None) -> int:
        """Get counter value."""
        key = self._make_key(name, tags)
        with self._lock:
            return self._counters.get(key, 0)
    
    def get_gauge(self, name: str, tags: Optional[Dict[str, str]] = None) -> Optional[float]:
        """Get gauge value."""
        key = self._make_key(name, tags)
        with self._lock:
            return self._gauges.get(key)
    
    def get_timings(self, name: str, tags: Optional[Dict[str, str]] = None, 
                    since: Optional[datetime] = None) -> list:
        """Get timing metrics."""
        key = self._make_key(name, tags)
        with self._lock:
            points = list(self._metrics.get(key, []))
            if since:
                points = [p for p in points if p.timestamp >= since]
            return points
    
    def get_summary_stats(self, name: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get summary statistics for a metric."""
        points = self.get_timings(name, tags)
        if not points:
            return {}
        
        values = [p.value for p in points]
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "p50": self._percentile(values, 50),
            "p95": self._percentile(values, 95),
            "p99": self._percentile(values, 99)
        }
    
    def _make_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """Create a unique key from name and tags."""
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name},{tag_str}"
    
    def _percentile(self, values: list, percentile: float) -> float:
        """Calculate percentile value."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]


class HealthChecker:
    """Application health status checker."""
    
    def __init__(self):
        self._checks: Dict[str, Any] = {}
    
    def register_check(self, name: str, check_func):
        """Register a health check function."""
        self._checks[name] = check_func
    
    def check_health(self) -> Dict[str, Any]:
        """Run all health checks and return status."""
        results = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        all_healthy = True
        for name, check_func in self._checks.items():
            try:
                start_time = time.time()
                result = check_func()
                duration = time.time() - start_time
                
                results["checks"][name] = {
                    "status": "healthy" if result else "unhealthy",
                    "duration": round(duration, 3),
                    "message": result if isinstance(result, str) else "OK"
                }
                
                if not result:
                    all_healthy = False
                    
            except Exception as e:
                results["checks"][name] = {
                    "status": "error",
                    "duration": 0,
                    "message": str(e)
                }
                all_healthy = False
        
        results["status"] = "healthy" if all_healthy else "unhealthy"
        return results


# Global metrics collector
metrics = MetricsCollector()

# Global health checker
health_checker = HealthChecker()


def timing_decorator(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """Decorator to automatically record function execution time."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                metrics.record_timing(metric_name, duration, tags)
        return wrapper
    return decorator


def counter_decorator(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """Decorator to automatically increment counter on function call."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            metrics.increment_counter(metric_name, tags=tags)
            return func(*args, **kwargs)
        return wrapper
    return decorator
