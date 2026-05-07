"""Alerting and notification system."""
import os
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from .metrics import metrics


@dataclass
class Alert:
    """Alert configuration."""
    name: str
    threshold: float
    comparison: str  # "gt", "lt", "eq"
    window_minutes: int = 5
    cooldown_minutes: int = 15
    last_sent: Optional[datetime] = None


class AlertManager:
    """Manages alerting based on metrics."""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.email_config = self._load_email_config()
    
    def register_alert(self, alert: Alert):
        """Register a new alert."""
        self.alerts[alert.name] = alert
    
    def check_alerts(self):
        """Check all registered alerts and send notifications if needed."""
        for alert_name, alert in self.alerts.items():
            if self._should_send_alert(alert):
                self._send_alert(alert)
                alert.last_sent = datetime.utcnow()
    
    def _should_send_alert(self, alert: Alert) -> bool:
        """Check if alert should be sent based on cooldown and threshold."""
        now = datetime.utcnow()
        
        # Check cooldown
        if alert.last_sent:
            cooldown_passed = (now - alert.last_sent) >= timedelta(minutes=alert.cooldown_minutes)
            if not cooldown_passed:
                return False
        
        # Check threshold
        recent_metrics = metrics.get_timings(
            alert.name,
            since=now - timedelta(minutes=alert.window_minutes)
        )
        
        if not recent_metrics:
            return False
        
        latest_value = recent_metrics[-1].value
        
        if alert.comparison == "gt":
            return latest_value > alert.threshold
        elif alert.comparison == "lt":
            return latest_value < alert.threshold
        elif alert.comparison == "eq":
            return latest_value == alert.threshold
        
        return False
    
    def _send_alert(self, alert: Alert):
        """Send alert notification."""
        message = self._create_alert_message(alert)
        
        if self.email_config:
            self._send_email_alert(alert.name, message)
        
        # Log the alert
        print(f"ALERT: {alert.name} - {message}")
    
    def _create_alert_message(self, alert: Alert) -> str:
        """Create alert message."""
        recent_metrics = metrics.get_timings(
            alert.name,
            since=datetime.utcnow() - timedelta(minutes=alert.window_minutes)
        )
        
        if not recent_metrics:
            return f"Alert {alert.name} triggered but no recent metrics available"
        
        latest_value = recent_metrics[-1].value
        timestamp = recent_metrics[-1].timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        return (
            f"ALERT: {alert.name}\n"
            f"Threshold: {alert.comparison} {alert.threshold}\n"
            f"Current Value: {latest_value}\n"
            f"Time: {timestamp}\n"
            f"Window: Last {alert.window_minutes} minutes"
        )
    
    def _load_email_config(self) -> Optional[Dict[str, str]]:
        """Load email configuration from environment."""
        if not all([
            os.getenv("SMTP_SERVER"),
            os.getenv("SMTP_PORT"),
            os.getenv("SMTP_USERNAME"),
            os.getenv("SMTP_PASSWORD"),
            os.getenv("ALERT_EMAIL_FROM"),
            os.getenv("ALERT_EMAIL_TO")
        ]):
            return None
        
        return {
            "server": os.getenv("SMTP_SERVER"),
            "port": os.getenv("SMTP_PORT"),
            "username": os.getenv("SMTP_USERNAME"),
            "password": os.getenv("SMTP_PASSWORD"),
            "from_email": os.getenv("ALERT_EMAIL_FROM"),
            "to_email": os.getenv("ALERT_EMAIL_TO")
        }
    
    def _send_email_alert(self, alert_name: str, message: str):
        """Send alert via email."""
        if not self.email_config:
            return
        
        try:
            msg = MimeMultipart()
            msg['From'] = self.email_config["from_email"]
            msg['To'] = self.email_config["to_email"]
            msg['Subject'] = f"Krishi Saarthi Alert: {alert_name}"
            
            body = MimeText(message, 'plain')
            msg.attach(body)
            
            server = smtplib.SMTP(self.email_config["server"], int(self.email_config["port"]))
            server.starttls()
            server.login(self.email_config["username"], self.email_config["password"])
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            print(f"Failed to send email alert: {e}")


# Global alert manager
alert_manager = AlertManager()


def register_default_alerts():
    """Register default alerts for the application."""
    # API response time alert
    alert_manager.register_alert(Alert(
        name="api_response_time",
        threshold=5.0,
        comparison="gt",
        window_minutes=5,
        cooldown_minutes=15
    ))
    
    # Database connection time alert
    alert_manager.register_alert(Alert(
        name="db_query_time",
        threshold=2.0,
        comparison="gt",
        window_minutes=5,
        cooldown_minutes=15
    ))
    
    # Error rate alert
    alert_manager.register_alert(Alert(
        name="error_rate",
        threshold=10.0,
        comparison="gt",
        window_minutes=5,
        cooldown_minutes=30
    ))
