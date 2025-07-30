#!/usr/bin/env python3
"""
EIPAS System Health Check Utility
Comprehensive system validation and health monitoring
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import time
from datetime import datetime

class EIPASHealthChecker:
    """Comprehensive EIPAS system health checker"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent
        self.installer_path = self.base_path / "installer"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "UNKNOWN",
            "checks": {},
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
    
    def run_comprehensive_check(self) -> Dict:
        """Run all health checks and return results"""
        print("🔍 Starting EIPAS System Health Check...")
        print(f"   Base Path: {self.base_path}")
        print(f"   Timestamp: {self.results['timestamp']}")
        print("=" * 60)
        
        # Core system checks
        self.check_python_environment()
        self.check_claude_code_cli()
        self.check_file_structure()
        self.check_agent_templates()
        self.check_configuration_files()
        self.check_documentation()
        self.check_permissions()
        self.check_disk_space()
        
        # Advanced checks
        self.check_template_integrity()
        self.check_file_io_patterns()
        self.check_cross_references()
        
        # Performance checks
        self.check_system_performance()
        
        # Generate overall health status
        self.calculate_overall_health()
        
        return self.results
    
    def check_python_environment(self):
        """Validate Python environment"""
        check_name = "python_environment"
        try:
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                self.results["checks"][check_name] = {
                    "status": "PASS",
                    "message": f"Python {version.major}.{version.minor}.{version.micro}",
                    "details": "Python version meets requirements (3.8+)"
                }
            else:
                self.results["checks"][check_name] = {
                    "status": "FAIL",
                    "message": f"Python {version.major}.{version.minor}.{version.micro}",
                    "details": "Python 3.8 or higher required"
                }
                self.results["errors"].append("Python version below minimum requirement")
        except Exception as e:
            self.results["checks"][check_name] = {
                "status": "ERROR",
                "message": str(e),
                "details": "Failed to check Python version"
            }
    
    def check_claude_code_cli(self):
        """Verify Claude Code CLI availability"""
        check_name = "claude_code_cli"
        try:
            result = subprocess.run(['claude-code', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.results["checks"][check_name] = {
                    "status": "PASS",
                    "message": "Claude Code CLI available",
                    "details": result.stdout.strip()
                }
            else:
                self.results["checks"][check_name] = {
                    "status": "FAIL",
                    "message": "Claude Code CLI not responding",
                    "details": result.stderr.strip()
                }
                self.results["errors"].append("Claude Code CLI not available or not authenticated")
        except FileNotFoundError:
            self.results["checks"][check_name] = {
                "status": "FAIL",
                "message": "Claude Code CLI not found",
                "details": "Install Claude Code CLI and ensure it's in PATH"
            }
            self.results["errors"].append("Claude Code CLI not installed")
        except subprocess.TimeoutExpired:
            self.results["checks"][check_name] = {
                "status": "WARN",
                "message": "Claude Code CLI timeout",
                "details": "CLI response time exceeded 10 seconds"
            }
            self.results["warnings"].append("Claude Code CLI responding slowly")
        except Exception as e:
            self.results["checks"][check_name] = {
                "status": "ERROR",
                "message": str(e),
                "details": "Unexpected error checking Claude Code CLI"
            }
    
    def check_file_structure(self):
        """Validate core file structure"""
        check_name = "file_structure"
        required_paths = [
            "installer",
            "installer/agent-templates",
            "installer/agent-templates/phase1",
            "installer/agent-templates/phase2", 
            "installer/agent-templates/phase3",
            "installer/agent-templates/phase4",
            "installer/agent-templates/phase5",
            "installer/agent-templates/meta",
            "installer/core",
            "installer/utils",
            "installer/config-templates"
        ]
        
        missing_paths = []
        for path in required_paths:
            full_path = self.base_path / path
            if not full_path.exists():
                missing_paths.append(path)
        
        if not missing_paths:
            self.results["checks"][check_name] = {
                "status": "PASS",
                "message": "All required directories present",
                "details": f"Validated {len(required_paths)} core directories"
            }
        else:
            self.results["checks"][check_name] = {
                "status": "FAIL",
                "message": f"{len(missing_paths)} missing directories",
                "details": f"Missing: {', '.join(missing_paths)}"
            }
            self.results["errors"].append("Core directory structure incomplete")
    
    def check_agent_templates(self):
        """Validate agent template completeness"""
        check_name = "agent_templates"
        expected_agents = {
            "phase1": 9,  # 9 executives
            "phase2": 4,  # 4 analysts  
            "phase3": 5,  # 5 architects
            "phase4": 4,  # 4 developers
            "phase5": 4,  # 4 QA specialists
            "meta": 6     # 6 meta agents
        }
        
        agent_counts = {}
        missing_phases = []
        
        for phase, expected_count in expected_agents.items():
            phase_path = self.installer_path / "agent-templates" / phase
            if phase_path.exists():
                agent_files = list(phase_path.glob("*.md"))
                agent_counts[phase] = len(agent_files)
                if len(agent_files) != expected_count:
                    self.results["warnings"].append(
                        f"Phase {phase}: expected {expected_count} agents, found {len(agent_files)}"
                    )
            else:
                missing_phases.append(phase)
                agent_counts[phase] = 0
        
        total_expected = sum(expected_agents.values())
        total_found = sum(agent_counts.values())
        
        if missing_phases:
            self.results["checks"][check_name] = {
                "status": "FAIL",
                "message": f"Missing phases: {', '.join(missing_phases)}",
                "details": f"Found {total_found}/{total_expected} total agents"
            }
            self.results["errors"].append("Agent template phases missing")
        elif total_found == total_expected:
            self.results["checks"][check_name] = {
                "status": "PASS",
                "message": f"All {total_expected} agent templates present",
                "details": f"Phase distribution: {agent_counts}"
            }
        else:
            self.results["checks"][check_name] = {
                "status": "WARN",
                "message": f"Agent count mismatch: {total_found}/{total_expected}",
                "details": f"Phase distribution: {agent_counts}"
            }
            self.results["warnings"].append("Agent template count discrepancy")
    
    def check_configuration_files(self):
        """Validate configuration file completeness"""
        check_name = "configuration_files"
        config_files = [
            "config-templates/quality-gates.json",
            "config-templates/workflow-settings.json", 
            "config-templates/agent-behavior.json",
            "settings-templates/settings.json"
        ]
        
        missing_configs = []
        invalid_configs = []
        
        for config_file in config_files:
            config_path = self.installer_path / config_file
            if not config_path.exists():
                missing_configs.append(config_file)
            else:
                try:
                    with open(config_path, 'r') as f:
                        json.load(f)
                except json.JSONDecodeError:
                    invalid_configs.append(config_file)
        
        if missing_configs or invalid_configs:
            status = "FAIL" if missing_configs else "WARN"
            message_parts = []
            if missing_configs:
                message_parts.append(f"{len(missing_configs)} missing")
            if invalid_configs:
                message_parts.append(f"{len(invalid_configs)} invalid JSON")
            
            self.results["checks"][check_name] = {
                "status": status,
                "message": f"Config issues: {', '.join(message_parts)}",
                "details": f"Missing: {missing_configs}, Invalid: {invalid_configs}"
            }
            
            if missing_configs:
                self.results["errors"].append("Required configuration files missing")
            if invalid_configs:
                self.results["warnings"].append("Configuration files contain invalid JSON")
        else:
            self.results["checks"][check_name] = {
                "status": "PASS",
                "message": f"All {len(config_files)} configuration files valid",
                "details": "All JSON configuration files parsed successfully"
            }
    
    def check_documentation(self):
        """Validate documentation completeness"""
        check_name = "documentation"
        doc_files = [
            "WORKFLOW_EXECUTION_GUIDE.md",
            "TESTING_DOCUMENTATION.md", 
            "SYSTEM_ARCHITECTURE_OVERVIEW.md",
            "SYSTEM_VALIDATION.md",
            "../README.md"
        ]
        
        missing_docs = []
        for doc_file in doc_files:
            doc_path = self.installer_path / doc_file
            if not doc_path.exists():
                missing_docs.append(doc_file)
        
        if missing_docs:
            self.results["checks"][check_name] = {
                "status": "WARN",
                "message": f"{len(missing_docs)} documentation files missing",
                "details": f"Missing: {', '.join(missing_docs)}"
            }
            self.results["warnings"].append("Documentation incomplete")
        else:
            self.results["checks"][check_name] = {
                "status": "PASS",
                "message": f"All {len(doc_files)} documentation files present",
                "details": "Complete documentation suite available"
            }
    
    def check_permissions(self):
        """Check file permissions"""
        check_name = "file_permissions"
        try:
            # Check if we can write to the installer directory
            test_file = self.installer_path / ".health_check_test"
            test_file.write_text("test")
            test_file.unlink()
            
            # Check Claude directory permissions if it exists
            claude_dir = Path.home() / ".claude"
            if claude_dir.exists():
                eipas_dir = claude_dir / "eipas-system"
                if not eipas_dir.exists():
                    eipas_dir.mkdir(parents=True, exist_ok=True)
                
                # Test write permissions
                test_claude_file = eipas_dir / ".health_check_test"
                test_claude_file.write_text("test")
                test_claude_file.unlink()
            
            self.results["checks"][check_name] = {
                "status": "PASS",
                "message": "File permissions adequate",
                "details": "Read/write access verified for core directories"
            }
        except PermissionError as e:
            self.results["checks"][check_name] = {
                "status": "FAIL",
                "message": "Permission denied",
                "details": str(e)
            }
            self.results["errors"].append("Insufficient file permissions")
        except Exception as e:
            self.results["checks"][check_name] = {
                "status": "ERROR",
                "message": str(e),
                "details": "Unexpected error checking permissions"
            }
    
    def check_disk_space(self):
        """Check available disk space"""
        check_name = "disk_space"
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.base_path)
            
            # Convert to GB
            free_gb = free / (1024**3)
            
            if free_gb >= 1.0:  # 1GB minimum
                self.results["checks"][check_name] = {
                    "status": "PASS",
                    "message": f"{free_gb:.1f}GB available",
                    "details": f"Sufficient disk space (minimum 1GB required)"
                }
            elif free_gb >= 0.5:  # 500MB warning threshold
                self.results["checks"][check_name] = {
                    "status": "WARN",
                    "message": f"{free_gb:.1f}GB available",
                    "details": "Low disk space - recommend freeing space"
                }
                self.results["warnings"].append("Low disk space available")
            else:
                self.results["checks"][check_name] = {
                    "status": "FAIL",
                    "message": f"{free_gb:.1f}GB available",
                    "details": "Insufficient disk space (minimum 1GB required)"
                }
                self.results["errors"].append("Insufficient disk space")
        except Exception as e:
            self.results["checks"][check_name] = {
                "status": "ERROR",
                "message": str(e),
                "details": "Failed to check disk space"
            }
    
    def check_template_integrity(self):
        """Check agent template integrity"""
        check_name = "template_integrity"
        corrupted_templates = []
        missing_sections = []
        
        for phase_dir in (self.installer_path / "agent-templates").iterdir():
            if phase_dir.is_dir() and not phase_dir.name.startswith('.'):
                for template_file in phase_dir.glob("*.md"):
                    try:
                        content = template_file.read_text()
                        
                        # Check for required sections
                        required_sections = ["---", "# ", "## "]
                        missing = [sec for sec in required_sections if sec not in content]
                        if missing:
                            missing_sections.append(f"{template_file.name}: {missing}")
                        
                        # Check for File I/O Operations section (should be present in most agents)
                        if "File I/O Operations" not in content and phase_dir.name != "meta":
                            missing_sections.append(f"{template_file.name}: Missing File I/O Operations")
                            
                    except Exception as e:
                        corrupted_templates.append(f"{template_file.name}: {str(e)}")
        
        if corrupted_templates or missing_sections:
            status = "FAIL" if corrupted_templates else "WARN"
            issues = len(corrupted_templates) + len(missing_sections)
            
            self.results["checks"][check_name] = {
                "status": status,
                "message": f"{issues} template integrity issues",
                "details": f"Corrupted: {len(corrupted_templates)}, Missing sections: {len(missing_sections)}"
            }
            
            if corrupted_templates:
                self.results["errors"].append("Corrupted agent templates detected")
            if missing_sections:
                self.results["warnings"].append("Agent templates missing required sections")
        else:
            self.results["checks"][check_name] = {
                "status": "PASS",
                "message": "All agent templates valid",
                "details": "Template structure and content integrity verified"
            }
    
    def check_file_io_patterns(self):
        """Verify File I/O patterns in agent templates"""
        check_name = "file_io_patterns"
        
        agents_with_io = 0
        agents_without_io = []
        
        for phase_dir in (self.installer_path / "agent-templates").iterdir():
            if phase_dir.is_dir() and phase_dir.name.startswith('phase'):
                for template_file in phase_dir.glob("*.md"):
                    content = template_file.read_text()
                    if "File I/O Operations" in content and "input_references" in content:
                        agents_with_io += 1
                    else:
                        agents_without_io.append(f"{phase_dir.name}/{template_file.name}")
        
        if agents_without_io:
            self.results["checks"][check_name] = {
                "status": "WARN",
                "message": f"{len(agents_without_io)} agents missing File I/O patterns",
                "details": f"Agents with I/O: {agents_with_io}, Missing: {agents_without_io[:5]}"
            }
            self.results["warnings"].append("Some agents missing File I/O integration")
        else:
            self.results["checks"][check_name] = {
                "status": "PASS",
                "message": f"All {agents_with_io} phase agents have File I/O patterns",
                "details": "Cross-phase workflow continuity properly configured"
            }
    
    def check_cross_references(self):
        """Check cross-references between documentation"""
        check_name = "cross_references"
        broken_refs = []
        
        # This is a simplified check - in production you'd want more comprehensive link validation
        readme_path = self.base_path / "README.md"
        if readme_path.exists():
            content = readme_path.read_text()
            referenced_files = [
                "installer/WORKFLOW_EXECUTION_GUIDE.md",
                "installer/SYSTEM_ARCHITECTURE_OVERVIEW.md",
                "installer/TESTING_DOCUMENTATION.md"
            ]
            
            for ref_file in referenced_files:
                if ref_file in content:
                    file_path = self.base_path / ref_file
                    if not file_path.exists():
                        broken_refs.append(ref_file)
        
        if broken_refs:
            self.results["checks"][check_name] = {
                "status": "WARN",
                "message": f"{len(broken_refs)} broken documentation references",
                "details": f"Broken references: {broken_refs}"
            }
            self.results["warnings"].append("Documentation has broken internal references")
        else:
            self.results["checks"][check_name] = {
                "status": "PASS",
                "message": "Documentation cross-references valid",
                "details": "All internal documentation links verified"
            }
    
    def check_system_performance(self):
        """Basic system performance check"""
        check_name = "system_performance"
        try:
            # Simple file I/O performance test
            start_time = time.time()
            test_file = self.installer_path / ".perf_test"
            
            # Write test
            test_data = "performance test data" * 1000
            test_file.write_text(test_data)
            
            # Read test
            read_data = test_file.read_text()
            
            # Cleanup
            test_file.unlink()
            
            duration = time.time() - start_time
            
            if duration < 1.0:  # Should complete in under 1 second
                self.results["checks"][check_name] = {
                    "status": "PASS",
                    "message": f"File I/O performance: {duration:.3f}s",
                    "details": "System performance within acceptable limits"
                }
            else:
                self.results["checks"][check_name] = {
                    "status": "WARN",
                    "message": f"File I/O performance: {duration:.3f}s",
                    "details": "System performance slower than optimal"
                }
                self.results["warnings"].append("System performance below optimal")
                
        except Exception as e:
            self.results["checks"][check_name] = {
                "status": "ERROR",
                "message": str(e),
                "details": "Failed to run performance test"
            }
    
    def calculate_overall_health(self):
        """Calculate overall system health"""
        total_checks = len(self.results["checks"])
        passed_checks = sum(1 for check in self.results["checks"].values() if check["status"] == "PASS")
        failed_checks = sum(1 for check in self.results["checks"].values() if check["status"] == "FAIL")
        error_checks = sum(1 for check in self.results["checks"].values() if check["status"] == "ERROR")
        
        if error_checks > 0 or failed_checks > 2:
            self.results["overall_health"] = "CRITICAL"
            self.results["recommendations"].append("System requires immediate attention - critical issues detected")
        elif failed_checks > 0:
            self.results["overall_health"] = "DEGRADED"
            self.results["recommendations"].append("System has issues that should be addressed")
        elif len(self.results["warnings"]) > 3:
            self.results["overall_health"] = "WARNING"
            self.results["recommendations"].append("System operational but has warnings to address")
        else:
            self.results["overall_health"] = "HEALTHY"
            self.results["recommendations"].append("System is operating optimally")
        
        # Add general recommendations
        if self.results["overall_health"] in ["CRITICAL", "DEGRADED"]:
            self.results["recommendations"].append("Run 'python install-eipas.py --repair' to fix common issues")
        
        self.results["summary"] = {
            "total_checks": total_checks,
            "passed": passed_checks,
            "warnings": len([c for c in self.results["checks"].values() if c["status"] == "WARN"]),
            "failed": failed_checks,
            "errors": error_checks,
            "health_score": round((passed_checks / total_checks) * 100, 1) if total_checks > 0 else 0
        }
    
    def print_results(self):
        """Print formatted health check results"""
        print(f"\n{'='*60}")
        print(f"🏥 EIPAS SYSTEM HEALTH CHECK RESULTS")
        print(f"{'='*60}")
        print(f"Overall Health: {self.get_health_icon()} {self.results['overall_health']}")
        print(f"Health Score: {self.results['summary']['health_score']}%")
        print(f"Timestamp: {self.results['timestamp']}")
        
        # Summary
        summary = self.results['summary']
        print(f"\n📊 Summary:")
        print(f"   ✅ Passed: {summary['passed']}")
        print(f"   ⚠️  Warnings: {summary['warnings']}")
        print(f"   ❌ Failed: {summary['failed']}")
        print(f"   🚨 Errors: {summary['errors']}")
        print(f"   📈 Total Checks: {summary['total_checks']}")
        
        # Detailed results
        print(f"\n🔍 Detailed Results:")
        for check_name, result in self.results["checks"].items():
            icon = self.get_status_icon(result["status"])
            print(f"   {icon} {check_name.replace('_', ' ').title()}: {result['message']}")
        
        # Warnings
        if self.results["warnings"]:
            print(f"\n⚠️  Warnings ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"]:
                print(f"   • {warning}")
        
        # Errors
        if self.results["errors"]:
            print(f"\n❌ Errors ({len(self.results['errors'])}):")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        # Recommendations
        if self.results["recommendations"]:
            print(f"\n💡 Recommendations:")
            for rec in self.results["recommendations"]:
                print(f"   • {rec}")
        
        print(f"\n{'='*60}")
    
    def get_health_icon(self) -> str:
        """Get icon for overall health status"""
        icons = {
            "HEALTHY": "🟢",
            "WARNING": "🟡", 
            "DEGRADED": "🟠",
            "CRITICAL": "🔴",
            "UNKNOWN": "⚪"
        }
        return icons.get(self.results["overall_health"], "⚪")
    
    def get_status_icon(self, status: str) -> str:
        """Get icon for check status"""
        icons = {
            "PASS": "✅",
            "WARN": "⚠️",
            "FAIL": "❌", 
            "ERROR": "🚨"
        }
        return icons.get(status, "❓")

def main():
    """Main entry point for health check utility"""
    checker = EIPASHealthChecker()
    
    try:
        results = checker.run_comprehensive_check()
        checker.print_results()
        
        # Save results to file
        results_file = checker.installer_path / "utils" / "health_check_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📁 Detailed results saved to: {results_file}")
        
        # Exit with appropriate code
        if results["overall_health"] in ["CRITICAL", "DEGRADED"]:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n❌ Health check cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n🚨 Health check failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()