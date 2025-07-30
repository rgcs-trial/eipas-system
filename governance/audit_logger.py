"""
Enterprise Audit Logger

Comprehensive audit logging system for tracking configuration changes,
policy evaluations, user actions, and compliance events with tamper-evident logging.
"""

import json
import time
import hashlib
import hmac
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
import logging
import sqlite3
import threading
from cryptography.fernet import Fernet
import os

class AuditEventType(Enum):
    """Types of audit events"""
    CONFIG_CHANGE = "config_change"
    POLICY_EVALUATION = "policy_evaluation"
    COMPLIANCE_ASSESSMENT = "compliance_assessment"
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    SECURITY_EVENT = "security_event"
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    ERROR_EVENT = "error_event"

class AuditSeverity(Enum):
    """Audit event severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class AuditEvent:
    """Individual audit event"""
    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    severity: AuditSeverity
    user_id: Optional[str]
    session_id: Optional[str]
    source_ip: Optional[str]
    user_agent: Optional[str]
    resource: str
    action: str
    details: Dict[str, Any]
    outcome: str  # success, failure, partial
    risk_score: Optional[float] = None
    previous_hash: Optional[str] = None
    integrity_hash: Optional[str] = None

@dataclass
class AuditQuery:
    """Audit log query parameters"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_types: Optional[List[AuditEventType]] = None
    severities: Optional[List[AuditSeverity]] = None
    user_ids: Optional[List[str]] = None
    resources: Optional[List[str]] = None
    actions: Optional[List[str]] = None
    outcomes: Optional[List[str]] = None
    limit: int = 1000
    offset: int = 0

class AuditLogger:
    """Enterprise-grade audit logging system with integrity protection"""
    
    def __init__(self, db_path: str = "~/.claude/eipas-system/audit/audit.db",
                 encryption_key: Optional[bytes] = None):
        self.logger = logging.getLogger(__name__)
        
        # Setup database path
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup encryption
        if encryption_key:
            self.cipher = Fernet(encryption_key)
        else:
            # Generate or load encryption key
            key_path = self.db_path.parent / "audit.key"
            if key_path.exists():
                with open(key_path, 'rb') as f:
                    self.cipher = Fernet(f.read())
            else:
                key = Fernet.generate_key()
                with open(key_path, 'wb') as f:
                    f.write(key)
                os.chmod(key_path, 0o600)  # Restrict permissions
                self.cipher = Fernet(key)
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Initialize database
        self._init_database()
        
        # Chain integrity tracking
        self._last_hash = self._get_last_hash()
    
    def _init_database(self):
        """Initialize audit database schema"""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    source_ip TEXT,
                    user_agent TEXT,
                    resource TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    risk_score REAL,
                    previous_hash TEXT,
                    integrity_hash TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_events(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON audit_events(event_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON audit_events(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_resource ON audit_events(resource)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_severity ON audit_events(severity)")
            
            # Create audit trail integrity table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_integrity (
                    chain_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    block_hash TEXT NOT NULL,
                    event_count INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    merkle_root TEXT
                )
            """)
    
    def log_event(self, event_type: AuditEventType, resource: str, action: str,
                  details: Dict[str, Any], outcome: str = "success",
                  severity: AuditSeverity = AuditSeverity.INFO,
                  user_id: Optional[str] = None, session_id: Optional[str] = None,
                  source_ip: Optional[str] = None, user_agent: Optional[str] = None,
                  risk_score: Optional[float] = None) -> str:
        """Log an audit event with integrity protection"""
        
        with self._lock:
            # Generate unique event ID
            event_id = self._generate_event_id()
            
            # Create audit event
            event = AuditEvent(
                event_id=event_id,
                timestamp=datetime.now(timezone.utc),
                event_type=event_type,
                severity=severity,
                user_id=user_id,
                session_id=session_id,
                source_ip=source_ip,
                user_agent=user_agent,
                resource=resource,
                action=action,
                details=details,
                outcome=outcome,
                risk_score=risk_score,
                previous_hash=self._last_hash
            )
            
            # Calculate integrity hash
            event.integrity_hash = self._calculate_integrity_hash(event)
            
            # Store event
            self._store_event(event)
            
            # Update chain hash
            self._last_hash = event.integrity_hash
            
            # Log to standard logger for immediate visibility
            log_level = self._severity_to_log_level(severity)
            self.logger.log(log_level, 
                           f"AUDIT: {event_type.value} - {resource}/{action} - {outcome} - User: {user_id}")
            
            return event_id
    
    def log_config_change(self, config_path: str, change_type: str, 
                         old_config: Optional[Dict] = None, new_config: Optional[Dict] = None,
                         user_id: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """Log configuration change event"""
        
        details = {
            "config_path": config_path,
            "change_type": change_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Add config diffs for security
        if old_config and new_config:
            details["config_diff"] = self._calculate_config_diff(old_config, new_config)
        
        if old_config:
            details["old_config_hash"] = hashlib.sha256(
                json.dumps(old_config, sort_keys=True).encode()
            ).hexdigest()
        
        if new_config:
            details["new_config_hash"] = hashlib.sha256(
                json.dumps(new_config, sort_keys=True).encode()
            ).hexdigest()
        
        return self.log_event(
            event_type=AuditEventType.CONFIG_CHANGE,
            resource=config_path,
            action=change_type,
            details=details,
            severity=AuditSeverity.MEDIUM,
            user_id=user_id,
            session_id=session_id
        )
    
    def log_policy_evaluation(self, policy_name: str, framework: str, 
                            violation_count: int, compliance_score: float,
                            user_id: Optional[str] = None) -> str:
        """Log policy evaluation event"""
        
        details = {
            "policy_name": policy_name,
            "framework": framework,
            "violation_count": violation_count,
            "compliance_score": compliance_score,
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Determine severity based on violations
        if violation_count == 0:
            severity = AuditSeverity.INFO
        elif violation_count <= 3:
            severity = AuditSeverity.LOW
        elif violation_count <= 10:
            severity = AuditSeverity.MEDIUM
        else:
            severity = AuditSeverity.HIGH
        
        return self.log_event(
            event_type=AuditEventType.POLICY_EVALUATION,
            resource=f"policy/{policy_name}",
            action="evaluate",
            details=details,
            outcome="success" if violation_count == 0 else "violations_found",
            severity=severity,
            user_id=user_id,
            risk_score=max(0.0, 1.0 - (compliance_score / 100.0))
        )
    
    def log_security_event(self, event_description: str, resource: str,
                          threat_level: str = "medium", details: Optional[Dict] = None,
                          user_id: Optional[str] = None, source_ip: Optional[str] = None) -> str:
        """Log security-related event"""
        
        event_details = {
            "event_description": event_description,
            "threat_level": threat_level,
            "detection_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if details:
            event_details.update(details)
        
        # Map threat level to severity
        severity_map = {
            "critical": AuditSeverity.CRITICAL,
            "high": AuditSeverity.HIGH,
            "medium": AuditSeverity.MEDIUM,
            "low": AuditSeverity.LOW
        }
        
        return self.log_event(
            event_type=AuditEventType.SECURITY_EVENT,
            resource=resource,
            action="security_detection",
            details=event_details,
            outcome="detected",
            severity=severity_map.get(threat_level, AuditSeverity.MEDIUM),
            user_id=user_id,
            source_ip=source_ip,
            risk_score={"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.2}.get(threat_level, 0.5)
        )
    
    def log_access_event(self, resource: str, action: str, granted: bool,
                        user_id: Optional[str] = None, session_id: Optional[str] = None,
                        source_ip: Optional[str] = None, reason: Optional[str] = None) -> str:
        """Log access control event"""
        
        details = {
            "access_timestamp": datetime.now(timezone.utc).isoformat(),
            "granted": granted
        }
        
        if reason:
            details["reason"] = reason
        
        event_type = AuditEventType.ACCESS_GRANTED if granted else AuditEventType.ACCESS_DENIED
        severity = AuditSeverity.INFO if granted else AuditSeverity.MEDIUM
        
        return self.log_event(
            event_type=event_type,
            resource=resource,
            action=action,
            details=details,
            outcome="granted" if granted else "denied",
            severity=severity,
            user_id=user_id,
            session_id=session_id,
            source_ip=source_ip
        )
    
    def query_events(self, query: AuditQuery) -> List[AuditEvent]:
        """Query audit events with filtering"""
        
        sql_parts = ["SELECT * FROM audit_events WHERE 1=1"]
        params = []
        
        # Build WHERE clause
        if query.start_time:
            sql_parts.append("AND timestamp >= ?")
            params.append(query.start_time.isoformat())
        
        if query.end_time:
            sql_parts.append("AND timestamp <= ?")
            params.append(query.end_time.isoformat())
        
        if query.event_types:
            placeholders = ','.join('?' * len(query.event_types))
            sql_parts.append(f"AND event_type IN ({placeholders})")
            params.extend([et.value for et in query.event_types])
        
        if query.severities:
            placeholders = ','.join('?' * len(query.severities))
            sql_parts.append(f"AND severity IN ({placeholders})")
            params.extend([s.value for s in query.severities])
        
        if query.user_ids:
            placeholders = ','.join('?' * len(query.user_ids))
            sql_parts.append(f"AND user_id IN ({placeholders})")
            params.extend(query.user_ids)
        
        if query.resources:
            placeholders = ','.join('?' * len(query.resources))
            sql_parts.append(f"AND resource IN ({placeholders})")
            params.extend(query.resources)
        
        if query.actions:
            placeholders = ','.join('?' * len(query.actions))
            sql_parts.append(f"AND action IN ({placeholders})")
            params.extend(query.actions)
        
        if query.outcomes:
            placeholders = ','.join('?' * len(query.outcomes))
            sql_parts.append(f"AND outcome IN ({placeholders})")
            params.extend(query.outcomes)
        
        # Add ordering and pagination
        sql_parts.append("ORDER BY timestamp DESC")
        sql_parts.append("LIMIT ? OFFSET ?")
        params.extend([query.limit, query.offset])
        
        sql = " ".join(sql_parts)
        
        events = []
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(sql, params)
                
                for row in cursor:
                    # Decrypt details if necessary
                    details_str = row['details']
                    if details_str.startswith('gAAAAA'):  # Fernet encrypted data marker
                        details = json.loads(self.cipher.decrypt(details_str.encode()).decode())
                    else:
                        details = json.loads(details_str)
                    
                    event = AuditEvent(
                        event_id=row['event_id'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        event_type=AuditEventType(row['event_type']),
                        severity=AuditSeverity(row['severity']),
                        user_id=row['user_id'],
                        session_id=row['session_id'],
                        source_ip=row['source_ip'],
                        user_agent=row['user_agent'],
                        resource=row['resource'],
                        action=row['action'],
                        details=details,
                        outcome=row['outcome'],
                        risk_score=row['risk_score'],
                        previous_hash=row['previous_hash'],
                        integrity_hash=row['integrity_hash']
                    )
                    events.append(event)
        
        except Exception as e:
            self.logger.error(f"Error querying audit events: {e}")
        
        return events
    
    def verify_integrity(self, event_id: Optional[str] = None) -> Dict[str, Any]:
        """Verify audit log integrity"""
        
        verification_result = {
            "verified": True,
            "total_events": 0,
            "corrupted_events": [],
            "chain_breaks": [],
            "verification_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get events to verify
                if event_id:
                    cursor = conn.execute("SELECT * FROM audit_events WHERE event_id = ? ORDER BY timestamp", (event_id,))
                else:
                    cursor = conn.execute("SELECT * FROM audit_events ORDER BY timestamp")
                
                previous_hash = None
                
                for row in cursor:
                    verification_result["total_events"] += 1
                    
                    # Reconstruct event for hash verification
                    details_str = row['details']
                    if details_str.startswith('gAAAAA'):
                        details = json.loads(self.cipher.decrypt(details_str.encode()).decode())
                    else:
                        details = json.loads(details_str)
                    
                    event = AuditEvent(
                        event_id=row['event_id'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        event_type=AuditEventType(row['event_type']),
                        severity=AuditSeverity(row['severity']),
                        user_id=row['user_id'],
                        session_id=row['session_id'],
                        source_ip=row['source_ip'],
                        user_agent=row['user_agent'],
                        resource=row['resource'],
                        action=row['action'],
                        details=details,
                        outcome=row['outcome'],
                        risk_score=row['risk_score'],
                        previous_hash=row['previous_hash'],
                        integrity_hash=None  # Will be calculated
                    )
                    
                    # Verify integrity hash
                    calculated_hash = self._calculate_integrity_hash(event)
                    if calculated_hash != row['integrity_hash']:
                        verification_result["verified"] = False
                        verification_result["corrupted_events"].append({
                            "event_id": row['event_id'],
                            "expected_hash": row['integrity_hash'],
                            "calculated_hash": calculated_hash
                        })
                    
                    # Verify chain integrity
                    if previous_hash is not None and row['previous_hash'] != previous_hash:
                        verification_result["verified"] = False
                        verification_result["chain_breaks"].append({
                            "event_id": row['event_id'],
                            "expected_previous": previous_hash,
                            "actual_previous": row['previous_hash']
                        })
                    
                    previous_hash = row['integrity_hash']
        
        except Exception as e:
            self.logger.error(f"Error verifying audit log integrity: {e}")
            verification_result["verified"] = False
            verification_result["error"] = str(e)
        
        return verification_result
    
    def export_audit_trail(self, query: AuditQuery, format: str = "json",
                          include_sensitive: bool = False) -> str:
        """Export audit trail for compliance reporting"""
        
        events = self.query_events(query)
        
        if format == "json":
            export_data = []
            for event in events:
                event_dict = asdict(event)
                event_dict['timestamp'] = event.timestamp.isoformat()
                event_dict['event_type'] = event.event_type.value
                event_dict['severity'] = event.severity.value
                
                # Optionally exclude sensitive details
                if not include_sensitive:
                    sensitive_keys = ['source_ip', 'user_agent', 'session_id']
                    for key in sensitive_keys:
                        if key in event_dict:
                            event_dict[key] = "[REDACTED]"
                
                export_data.append(event_dict)
            
            return json.dumps(export_data, indent=2)
        
        elif format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            if events:
                fieldnames = ['event_id', 'timestamp', 'event_type', 'severity', 
                            'user_id', 'resource', 'action', 'outcome']
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for event in events:
                    writer.writerow({
                        'event_id': event.event_id,
                        'timestamp': event.timestamp.isoformat(),
                        'event_type': event.event_type.value,
                        'severity': event.severity.value,
                        'user_id': event.user_id or '[SYSTEM]',
                        'resource': event.resource,
                        'action': event.action,
                        'outcome': event.outcome
                    })
            
            return output.getvalue()
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = str(int(time.time() * 1000000))  # microseconds
        random_part = os.urandom(8).hex()
        return f"audit_{timestamp}_{random_part}"
    
    def _calculate_integrity_hash(self, event: AuditEvent) -> str:
        """Calculate integrity hash for an event"""
        # Create canonical representation
        data = {
            'event_id': event.event_id,
            'timestamp': event.timestamp.isoformat(),
            'event_type': event.event_type.value,
            'severity': event.severity.value,
            'user_id': event.user_id,
            'resource': event.resource,
            'action': event.action,
            'details': event.details,
            'outcome': event.outcome,
            'previous_hash': event.previous_hash
        }
        
        canonical_json = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical_json.encode()).hexdigest()
    
    def _store_event(self, event: AuditEvent):
        """Store audit event in database"""
        # Encrypt sensitive details
        details_json = json.dumps(event.details)
        encrypted_details = self.cipher.encrypt(details_json.encode()).decode()
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                INSERT INTO audit_events 
                (event_id, timestamp, event_type, severity, user_id, session_id,
                 source_ip, user_agent, resource, action, details, outcome,
                 risk_score, previous_hash, integrity_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id,
                event.timestamp.isoformat(),
                event.event_type.value,
                event.severity.value,
                event.user_id,
                event.session_id,
                event.source_ip,
                event.user_agent,
                event.resource,
                event.action,
                encrypted_details,
                event.outcome,
                event.risk_score,
                event.previous_hash,
                event.integrity_hash
            ))
    
    def _get_last_hash(self) -> Optional[str]:
        """Get the hash of the last audit event"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute(
                    "SELECT integrity_hash FROM audit_events ORDER BY timestamp DESC LIMIT 1"
                )
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception:
            return None
    
    def _calculate_config_diff(self, old_config: Dict, new_config: Dict) -> Dict[str, Any]:
        """Calculate high-level diff between configurations"""
        diff = {
            "added": [],
            "removed": [],
            "modified": []
        }
        
        # Simple diff for audit purposes
        old_keys = set(old_config.keys())
        new_keys = set(new_config.keys())
        
        diff["added"] = list(new_keys - old_keys)
        diff["removed"] = list(old_keys - new_keys)
        
        for key in old_keys & new_keys:
            if old_config[key] != new_config[key]:
                diff["modified"].append(key)
        
        return diff
    
    def _severity_to_log_level(self, severity: AuditSeverity) -> int:
        """Convert audit severity to logging level"""
        mapping = {
            AuditSeverity.CRITICAL: logging.CRITICAL,
            AuditSeverity.HIGH: logging.ERROR,
            AuditSeverity.MEDIUM: logging.WARNING,
            AuditSeverity.LOW: logging.INFO,
            AuditSeverity.INFO: logging.INFO
        }
        return mapping.get(severity, logging.INFO)