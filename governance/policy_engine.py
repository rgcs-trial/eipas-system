"""
Enterprise Policy & Compliance Engine

Advanced governance system for enforcing organizational policies,
compliance standards, and security requirements across Claude Code configurations.
Provides automated policy validation, compliance reporting, and risk assessment.
"""

import json
import re
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import logging
import hashlib

class PolicySeverity(Enum):
    """Policy violation severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    NIST = "nist"
    CIS = "cis"
    CUSTOM = "custom"

@dataclass
class PolicyRule:
    """Individual policy rule definition"""
    id: str
    name: str
    description: str
    severity: PolicySeverity
    framework: ComplianceFramework
    rule_type: str  # 'allow', 'deny', 'require', 'limit'
    pattern: Optional[str] = None
    max_count: Optional[int] = None
    required_fields: Optional[List[str]] = None
    forbidden_patterns: Optional[List[str]] = None
    exceptions: Optional[List[str]] = None
    remediation: Optional[str] = None
    references: Optional[List[str]] = None

@dataclass
class PolicyViolation:
    """Policy violation details"""
    rule_id: str
    rule_name: str
    severity: PolicySeverity
    description: str
    location: str
    details: str
    remediation: str
    framework: ComplianceFramework
    timestamp: datetime = field(default_factory=datetime.now)
    auto_fixable: bool = False

@dataclass
class ComplianceReport:
    """Comprehensive compliance assessment report"""
    organization: str
    assessment_date: datetime
    frameworks: List[ComplianceFramework]
    overall_score: float  # 0-100
    violations: List[PolicyViolation]
    compliance_scores: Dict[ComplianceFramework, float]
    risk_level: str
    recommendations: List[str]
    next_assessment_due: datetime
    certification_status: Dict[ComplianceFramework, str]

class EnterprisePolicy:
    """Container for enterprise policy configuration"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.rules: List[PolicyRule] = []
        self.frameworks: Set[ComplianceFramework] = set()
        self.last_updated = datetime.now()
        self.approved_by: Optional[str] = None
        self.effective_date: Optional[datetime] = None
    
    def add_rule(self, rule: PolicyRule):
        """Add a policy rule"""
        self.rules.append(rule)
        self.frameworks.add(rule.framework)
        self.last_updated = datetime.now()
    
    def get_rules_by_framework(self, framework: ComplianceFramework) -> List[PolicyRule]:
        """Get all rules for a specific framework"""
        return [rule for rule in self.rules if rule.framework == framework]
    
    def get_critical_rules(self) -> List[PolicyRule]:
        """Get all critical severity rules"""
        return [rule for rule in self.rules if rule.severity == PolicySeverity.CRITICAL]

class PolicyEngine:
    """Advanced enterprise policy and compliance engine"""
    
    def __init__(self, organization: str = "Enterprise"):
        self.logger = logging.getLogger(__name__)
        self.organization = organization
        self.policies: Dict[str, EnterprisePolicy] = {}
        self.compliance_cache: Dict[str, ComplianceReport] = {}
        
        # Built-in compliance frameworks
        self._initialize_compliance_frameworks()
        
        # Risk assessment weights
        self.risk_weights = {
            PolicySeverity.CRITICAL: 10.0,
            PolicySeverity.HIGH: 5.0,
            PolicySeverity.MEDIUM: 2.0,
            PolicySeverity.LOW: 1.0,
            PolicySeverity.INFO: 0.0
        }
    
    def _initialize_compliance_frameworks(self):
        """Initialize built-in compliance framework policies"""
        
        # SOC 2 Type II Policy
        soc2_policy = EnterprisePolicy("SOC2_Type_II", "2024.1")
        
        soc2_policy.add_rule(PolicyRule(
            id="SOC2-AC-01",
            name="Access Control Restrictions",
            description="Tool permissions must follow principle of least privilege",
            severity=PolicySeverity.HIGH,
            framework=ComplianceFramework.SOC2,
            rule_type="deny",
            pattern=r"permissions.*allow.*\[\]",
            remediation="Restrict tool permissions to specific commands or patterns",
            references=["SOC 2 CC6.1", "SOC 2 CC6.2"]
        ))
        
        soc2_policy.add_rule(PolicyRule(
            id="SOC2-AC-02", 
            name="Dangerous Command Prevention",
            description="Prevent execution of dangerous system commands",
            severity=PolicySeverity.CRITICAL,
            framework=ComplianceFramework.SOC2,
            rule_type="deny",
            forbidden_patterns=[
                r"rm\s+-rf\s+/",
                r"sudo\s+rm",
                r"chmod\s+777",
                r"curl.*\|.*bash"
            ],
            remediation="Remove dangerous command patterns from configuration",
            references=["SOC 2 CC6.1"]
        ))
        
        soc2_policy.add_rule(PolicyRule(
            id="SOC2-DM-01",
            name="Data Minimization",
            description="Configurations should not contain sensitive data",
            severity=PolicySeverity.CRITICAL,
            framework=ComplianceFramework.SOC2,
            rule_type="deny",
            forbidden_patterns=[
                r"password",
                r"api[_-]?key",
                r"secret[_-]?key",
                r"access[_-]?token"
            ],
            remediation="Use environment variables or secure secret management",
            references=["SOC 2 CC6.7"]
        ))
        
        # ISO 27001 Policy
        iso_policy = EnterprisePolicy("ISO27001", "2024.1")
        
        iso_policy.add_rule(PolicyRule(
            id="ISO-AC-01",
            name="Information Security Management",
            description="Configurations must include security validation",
            severity=PolicySeverity.HIGH,
            framework=ComplianceFramework.ISO27001,
            rule_type="require",
            required_fields=["security_validation", "audit_logging"],
            remediation="Add security validation and audit logging to configuration",
            references=["ISO 27001:2022 A.9.1"]
        ))
        
        iso_policy.add_rule(PolicyRule(
            id="ISO-RA-01",
            name="Risk Assessment Documentation",
            description="High-risk configurations require documented risk assessment",
            severity=PolicySeverity.MEDIUM,
            framework=ComplianceFramework.ISO27001,
            rule_type="require",
            pattern=r"risk_assessment.*documented",
            remediation="Document risk assessment for configuration changes",
            references=["ISO 27001:2022 A.8.2"]
        ))
        
        # GDPR Policy
        gdpr_policy = EnterprisePolicy("GDPR_Compliance", "2024.1")
        
        gdpr_policy.add_rule(PolicyRule(
            id="GDPR-PP-01", 
            name="Privacy by Design",
            description="Data processing configurations must implement privacy by design",
            severity=PolicySeverity.HIGH,
            framework=ComplianceFramework.GDPR,
            rule_type="require",
            required_fields=["data_minimization", "purpose_limitation"],
            remediation="Implement privacy by design principles",
            references=["GDPR Article 25"]
        ))
        
        gdpr_policy.add_rule(PolicyRule(
            id="GDPR-DT-01",
            name="Data Transfer Restrictions", 
            description="Prevent unauthorized data transfers outside EU",
            severity=PolicySeverity.CRITICAL,
            framework=ComplianceFramework.GDPR,
            rule_type="deny",
            forbidden_patterns=[
                r"transfer.*non-eu",
                r"export.*outside.*eu",
                r"third.*country.*transfer"
            ],
            remediation="Ensure adequate safeguards for international transfers",
            references=["GDPR Chapter V"]
        ))
        
        # NIST Cybersecurity Framework
        nist_policy = EnterprisePolicy("NIST_CSF", "2024.1")
        
        nist_policy.add_rule(PolicyRule(
            id="NIST-ID-01",
            name="Asset Inventory",
            description="All tools and agents must be properly inventoried",
            severity=PolicySeverity.MEDIUM,
            framework=ComplianceFramework.NIST,
            rule_type="require",
            required_fields=["tool_inventory", "agent_registry"],
            remediation="Maintain comprehensive inventory of tools and agents",
            references=["NIST CSF ID.AM"]
        ))
        
        nist_policy.add_rule(PolicyRule(
            id="NIST-PR-01",
            name="Access Control Implementation",
            description="Implement appropriate access controls",
            severity=PolicySeverity.HIGH,
            framework=ComplianceFramework.NIST,
            rule_type="require",
            pattern=r"access_control.*implemented",
            remediation="Implement role-based access controls",
            references=["NIST CSF PR.AC"]
        ))
        
        # Register policies
        self.policies["soc2"] = soc2_policy
        self.policies["iso27001"] = iso_policy
        self.policies["gdpr"] = gdpr_policy
        self.policies["nist"] = nist_policy
    
    def evaluate_compliance(self, config: Dict, frameworks: List[ComplianceFramework],
                          policy_overrides: Optional[Dict] = None) -> ComplianceReport:
        """Evaluate configuration compliance against specified frameworks"""
        self.logger.info(f"Evaluating compliance for {len(frameworks)} frameworks")
        
        violations = []
        compliance_scores = {}
        
        # Evaluate each framework
        for framework in frameworks:
            framework_violations = self._evaluate_framework(config, framework, policy_overrides)
            violations.extend(framework_violations)
            
            # Calculate framework compliance score
            compliance_scores[framework] = self._calculate_framework_score(framework_violations, framework)
        
        # Calculate overall compliance score
        overall_score = sum(compliance_scores.values()) / len(compliance_scores) if compliance_scores else 0.0
        
        # Determine risk level
        risk_level = self._determine_risk_level(violations)
        
        # Generate recommendations
        recommendations = self._generate_compliance_recommendations(violations, frameworks)
        
        # Determine certification status
        certification_status = self._assess_certification_status(compliance_scores)
        
        report = ComplianceReport(
            organization=self.organization,
            assessment_date=datetime.now(),
            frameworks=frameworks,
            overall_score=overall_score,
            violations=violations,
            compliance_scores=compliance_scores,
            risk_level=risk_level,
            recommendations=recommendations,
            next_assessment_due=datetime.now() + timedelta(days=90),
            certification_status=certification_status
        )
        
        # Cache the report
        cache_key = self._generate_cache_key(config, frameworks)
        self.compliance_cache[cache_key] = report
        
        self.logger.info(f"Compliance evaluation complete: {overall_score:.1f}% compliance")
        return report
    
    def _evaluate_framework(self, config: Dict, framework: ComplianceFramework, 
                          policy_overrides: Optional[Dict] = None) -> List[PolicyViolation]:
        """Evaluate configuration against a specific compliance framework"""
        violations = []
        
        # Get policy for framework
        policy_key = framework.value
        if policy_key not in self.policies:
            self.logger.warning(f"No policy defined for framework: {framework.value}")
            return violations
        
        policy = self.policies[policy_key]
        config_str = json.dumps(config, indent=2)
        
        # Evaluate each rule
        for rule in policy.rules:
            # Apply policy overrides if provided
            if policy_overrides and rule.id in policy_overrides:
                if policy_overrides[rule.id].get('skip', False):
                    continue
                # Apply override modifications
                rule = self._apply_rule_override(rule, policy_overrides[rule.id])
            
            rule_violations = self._evaluate_rule(config, config_str, rule)
            violations.extend(rule_violations)
        
        return violations
    
    def _evaluate_rule(self, config: Dict, config_str: str, rule: PolicyRule) -> List[PolicyViolation]:
        """Evaluate a single policy rule against configuration"""
        violations = []
        
        if rule.rule_type == "deny":
            violations.extend(self._evaluate_deny_rule(config, config_str, rule))
        elif rule.rule_type == "require":
            violations.extend(self._evaluate_require_rule(config, config_str, rule))
        elif rule.rule_type == "limit":
            violations.extend(self._evaluate_limit_rule(config, config_str, rule))
        elif rule.rule_type == "allow":
            violations.extend(self._evaluate_allow_rule(config, config_str, rule))
        
        return violations
    
    def _evaluate_deny_rule(self, config: Dict, config_str: str, rule: PolicyRule) -> List[PolicyViolation]:
        """Evaluate deny-type policy rules"""
        violations = []
        
        # Check forbidden patterns
        if rule.forbidden_patterns:
            for pattern in rule.forbidden_patterns:
                matches = re.findall(pattern, config_str, re.IGNORECASE)
                if matches:
                    violations.append(PolicyViolation(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        severity=rule.severity,
                        description=f"Forbidden pattern detected: {pattern}",
                        location="configuration",
                        details=f"Found {len(matches)} matches: {matches[:3]}{'...' if len(matches) > 3 else ''}",
                        remediation=rule.remediation or "Remove forbidden patterns from configuration",
                        framework=rule.framework,
                        auto_fixable=True
                    ))
        
        # Check general pattern
        if rule.pattern:
            if re.search(rule.pattern, config_str, re.IGNORECASE):
                violations.append(PolicyViolation(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    description=rule.description,
                    location="configuration",
                    details=f"Configuration matches denied pattern: {rule.pattern}",
                    remediation=rule.remediation or "Modify configuration to avoid denied pattern",
                    framework=rule.framework
                ))
        
        return violations
    
    def _evaluate_require_rule(self, config: Dict, config_str: str, rule: PolicyRule) -> List[PolicyViolation]:
        """Evaluate require-type policy rules"""
        violations = []
        
        # Check required fields
        if rule.required_fields:
            for field in rule.required_fields:
                if not self._check_field_exists(config, field):
                    violations.append(PolicyViolation(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        severity=rule.severity,
                        description=f"Required field missing: {field}",
                        location="configuration",
                        details=f"Configuration must include '{field}' field",
                        remediation=rule.remediation or f"Add required field: {field}",
                        framework=rule.framework,
                        auto_fixable=True
                    ))
        
        # Check required pattern
        if rule.pattern:
            if not re.search(rule.pattern, config_str, re.IGNORECASE):
                violations.append(PolicyViolation(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    description=rule.description,
                    location="configuration",
                    details=f"Configuration missing required pattern: {rule.pattern}",
                    remediation=rule.remediation or "Add required pattern to configuration",
                    framework=rule.framework
                ))
        
        return violations
    
    def _evaluate_limit_rule(self, config: Dict, config_str: str, rule: PolicyRule) -> List[PolicyViolation]:
        """Evaluate limit-type policy rules"""
        violations = []
        
        if rule.max_count and rule.pattern:
            matches = re.findall(rule.pattern, config_str, re.IGNORECASE)
            if len(matches) > rule.max_count:
                violations.append(PolicyViolation(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    description=f"Exceeds maximum count: {len(matches)} > {rule.max_count}",
                    location="configuration",
                    details=f"Found {len(matches)} instances, maximum allowed: {rule.max_count}",
                    remediation=rule.remediation or f"Reduce count to {rule.max_count} or fewer",
                    framework=rule.framework
                ))
        
        return violations
    
    def _evaluate_allow_rule(self, config: Dict, config_str: str, rule: PolicyRule) -> List[PolicyViolation]:
        """Evaluate allow-type policy rules (informational)"""
        # Allow rules are generally informational and don't generate violations
        # They define what is explicitly permitted
        return []
    
    def _check_field_exists(self, config: Dict, field_path: str) -> bool:
        """Check if a nested field exists in configuration"""
        parts = field_path.split('.')
        current = config
        
        try:
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return False
            return True
        except (KeyError, TypeError):
            return False
    
    def _calculate_framework_score(self, violations: List[PolicyViolation], 
                                 framework: ComplianceFramework) -> float:
        """Calculate compliance score for a specific framework"""
        if not violations:
            return 100.0
        
        # Get total possible penalty points for this framework
        policy_key = framework.value
        if policy_key not in self.policies:
            return 100.0
        
        policy = self.policies[policy_key]
        max_penalty = sum(self.risk_weights[rule.severity] for rule in policy.rules)
        
        # Calculate actual penalties
        actual_penalty = sum(self.risk_weights[v.severity] for v in violations)
        
        # Calculate score (0-100)
        if max_penalty == 0:
            return 100.0
        
        score = max(0.0, 100.0 - (actual_penalty / max_penalty * 100.0))
        return round(score, 1)
    
    def _determine_risk_level(self, violations: List[PolicyViolation]) -> str:
        """Determine overall risk level based on violations"""
        if not violations:
            return "low"
        
        critical_count = sum(1 for v in violations if v.severity == PolicySeverity.CRITICAL)
        high_count = sum(1 for v in violations if v.severity == PolicySeverity.HIGH)
        
        if critical_count > 0:
            return "critical"
        elif high_count > 2:
            return "high"
        elif high_count > 0:
            return "medium"
        else:
            return "low"
    
    def _generate_compliance_recommendations(self, violations: List[PolicyViolation],
                                           frameworks: List[ComplianceFramework]) -> List[str]:
        """Generate compliance recommendations based on violations"""
        recommendations = []
        
        # Critical recommendations
        critical_violations = [v for v in violations if v.severity == PolicySeverity.CRITICAL]
        if critical_violations:
            recommendations.append(f"URGENT: Fix {len(critical_violations)} critical compliance violations immediately")
        
        # Framework-specific recommendations
        for framework in frameworks:
            framework_violations = [v for v in violations if v.framework == framework]
            if framework_violations:
                recommendations.append(f"Address {len(framework_violations)} {framework.value.upper()} compliance issues")
        
        # Auto-fixable recommendations
        auto_fixable = [v for v in violations if v.auto_fixable]
        if auto_fixable:
            recommendations.append(f"{len(auto_fixable)} violations can be automatically remediated")
        
        # General recommendations
        if len(violations) > 10:
            recommendations.append("Consider implementing automated compliance monitoring")
        
        if not recommendations:
            recommendations.append("Configuration meets all compliance requirements")
        
        return recommendations
    
    def _assess_certification_status(self, compliance_scores: Dict[ComplianceFramework, float]) -> Dict[ComplianceFramework, str]:
        """Assess certification readiness for each framework"""
        status = {}
        
        for framework, score in compliance_scores.items():
            if score >= 95.0:
                status[framework] = "certification_ready"
            elif score >= 85.0:
                status[framework] = "minor_gaps"
            elif score >= 70.0:
                status[framework] = "significant_gaps"
            else:
                status[framework] = "major_remediation_required"
        
        return status
    
    def _apply_rule_override(self, rule: PolicyRule, override: Dict) -> PolicyRule:
        """Apply policy override to a rule"""
        # Create a copy of the rule with overrides applied
        new_rule = PolicyRule(
            id=rule.id,
            name=rule.name,
            description=override.get('description', rule.description),
            severity=PolicySeverity(override.get('severity', rule.severity.value)),
            framework=rule.framework,
            rule_type=override.get('rule_type', rule.rule_type),
            pattern=override.get('pattern', rule.pattern),
            max_count=override.get('max_count', rule.max_count),
            required_fields=override.get('required_fields', rule.required_fields),
            forbidden_patterns=override.get('forbidden_patterns', rule.forbidden_patterns),
            exceptions=override.get('exceptions', rule.exceptions),
            remediation=override.get('remediation', rule.remediation),
            references=rule.references
        )
        
        return new_rule
    
    def _generate_cache_key(self, config: Dict, frameworks: List[ComplianceFramework]) -> str:
        """Generate cache key for compliance report"""
        config_hash = hashlib.md5(json.dumps(config, sort_keys=True).encode()).hexdigest()
        frameworks_str = '_'.join(sorted(f.value for f in frameworks))
        return f"{config_hash}_{frameworks_str}"
    
    def create_custom_policy(self, policy_name: str, rules: List[PolicyRule]) -> EnterprisePolicy:
        """Create a custom enterprise policy"""
        policy = EnterprisePolicy(policy_name)
        
        for rule in rules:
            policy.add_rule(rule)
        
        self.policies[policy_name.lower()] = policy
        self.logger.info(f"Created custom policy: {policy_name} with {len(rules)} rules")
        
        return policy
    
    def export_compliance_report(self, report: ComplianceReport, format: str = "json") -> str:
        """Export compliance report in specified format"""
        if format == "json":
            return json.dumps({
                "organization": report.organization,
                "assessment_date": report.assessment_date.isoformat(),
                "frameworks": [f.value for f in report.frameworks],
                "overall_score": report.overall_score,
                "violations": [{
                    "rule_id": v.rule_id,
                    "rule_name": v.rule_name,
                    "severity": v.severity.value,
                    "description": v.description,
                    "location": v.location,
                    "details": v.details,
                    "remediation": v.remediation,
                    "framework": v.framework.value,
                    "auto_fixable": v.auto_fixable
                } for v in report.violations],
                "compliance_scores": {f.value: score for f, score in report.compliance_scores.items()},
                "risk_level": report.risk_level,
                "recommendations": report.recommendations,
                "certification_status": {f.value: status for f, status in report.certification_status.items()}
            }, indent=2)
        
        elif format == "markdown":
            return self._generate_markdown_report(report)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _generate_markdown_report(self, report: ComplianceReport) -> str:
        """Generate markdown compliance report"""
        lines = [
            f"# Compliance Assessment Report",
            f"**Organization:** {report.organization}",
            f"**Assessment Date:** {report.assessment_date.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Overall Compliance Score:** {report.overall_score:.1f}%",
            f"**Risk Level:** {report.risk_level.upper()}",
            "",
            "## Framework Compliance Scores",
            ""
        ]
        
        for framework, score in report.compliance_scores.items():
            status = report.certification_status.get(framework, "unknown")
            lines.append(f"- **{framework.value.upper()}:** {score:.1f}% ({status.replace('_', ' ').title()})")
        
        lines.extend(["", "## Violations", ""])
        
        if not report.violations:
            lines.append("✅ No compliance violations found.")
        else:
            for violation in sorted(report.violations, key=lambda x: x.severity.value):
                lines.extend([
                    f"### {violation.rule_name} ({violation.severity.value.upper()})",
                    f"**Rule ID:** {violation.rule_id}",
                    f"**Framework:** {violation.framework.value.upper()}",
                    f"**Description:** {violation.description}",
                    f"**Details:** {violation.details}",
                    f"**Remediation:** {violation.remediation}",
                    ""
                ])
        
        lines.extend(["## Recommendations", ""])
        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"{i}. {rec}")
        
        return "\n".join(lines)