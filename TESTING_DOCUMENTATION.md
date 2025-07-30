# EIPAS Testing Documentation

## Overview

This document provides comprehensive testing procedures for validating the Enterprise Idea-to-Product Automation System (EIPAS) with Claude Code integration.

## Testing Strategy

### Testing Levels
1. **Unit Testing**: Individual agent validation
2. **Integration Testing**: Cross-phase workflow validation
3. **System Testing**: Complete end-to-end workflow testing
4. **User Acceptance Testing**: Interactive collaboration validation

### Testing Approaches
- **File I/O Validation**: Artifact creation and cross-phase reading
- **Interactive Flow Testing**: User approval gates and collaboration
- **Quality Gate Testing**: Threshold validation and advancement criteria
- **Error Handling**: Failure scenarios and recovery procedures

## Test Environment Setup

### Prerequisites
- Claude Code CLI installed and configured
- Python 3.8+ with standard library
- EIPAS system initialized with `python eipas.py init`
- Test workspace directory with write permissions

### Test Data Preparation
```bash
# Create test workspace
mkdir -p ~/.claude/eipas-system/workspace/test-workflow-001

# Prepare test idea file
cat > ~/.claude/eipas-system/workspace/test-workflow-001/idea.json << EOF
{
  "title": "AI-Powered Workflow Automation Platform",
  "description": "Enterprise platform for automating complex business workflows using AI-driven decision making",
  "industry": "Enterprise Software",
  "target_market": "Mid to large enterprises seeking workflow optimization",
  "initial_investment": "$2M",
  "expected_timeline": "18 months to market",
  "key_differentiators": ["AI-powered automation", "No-code workflow design", "Enterprise integration"],
  "user_context": {
    "submitter": "test-user",
    "timestamp": "2024-01-01T12:00:00Z",
    "priority": "high",
    "constraints": ["18-month timeline", "$2M budget", "SOC 2 compliance required"]
  }
}
EOF
```

## Individual Agent Testing

### Phase 1 Agent Testing Template

**Test Case: CEO Agent Evaluation**
```bash
# Test CEO agent with prepared idea
claude-code --template installer/agent-templates/phase1/ceo.md \
            --input workspace/test-workflow-001/idea.json
```

**Expected Behavior**:
1. Agent presents strategic evaluation criteria
2. Asks clarifying questions about business context
3. Waits for user approval: "Execute CEO evaluation with your input? (y/n)"
4. Produces structured output to `workspace/phase1/ceo-evaluation.json`

**Validation Checklist**:
- [ ] Interactive prompt displays correctly
- [ ] User input accepted and processed
- [ ] Output file created with proper JSON structure
- [ ] Evaluation score within 0-100 range
- [ ] Cross-phase references populated correctly

### File I/O Testing

**Test Case: Cross-Phase Reading Validation**
```bash
# Execute Phase 2 agent to test Phase 1 reading
claude-code --template installer/agent-templates/phase2/market-analyst.md \
            --workspace workspace/test-workflow-001
```

**Expected Behavior**:
1. Agent reads all Phase 1 executive evaluations
2. References specific insights from CEO, CTO, CFO evaluations
3. Builds analysis incorporating previous phase recommendations
4. Demonstrates cross-phase synthesis in output

**Validation Checklist**:
- [ ] All Phase 1 files successfully read
- [ ] Previous phase insights integrated into analysis
- [ ] Cross-phase synthesis section populated
- [ ] No file reading errors or missing references

## Integration Testing

### Cross-Phase Workflow Testing

**Test Case: Phase 1 → Phase 2 Integration**

**Setup**:
```bash
# Execute complete Phase 1
for agent in ceo cto cfo cmo coo chro legal-counsel strategy-vp innovation-director; do
    echo "Testing $agent agent..."
    claude-code --template installer/agent-templates/phase1/$agent.md \
                --workspace workspace/test-workflow-001
done

# Validate Phase 1 completion
python eipas.py validate-phase 1 --workspace test-workflow-001
```

**Execute Phase 2**:
```bash
# Execute Phase 2 with Phase 1 dependencies
for agent in market-analyst business-analyst competitive-analyst risk-analyst; do
    echo "Testing $agent with Phase 1 context..."
    claude-code --template installer/agent-templates/phase2/$agent.md \
                --workspace workspace/test-workflow-001
done
```

**Validation**:
- [ ] All Phase 2 agents successfully read Phase 1 outputs
- [ ] Market analysis incorporates CEO strategic priorities
- [ ] Business model aligns with CFO financial constraints
- [ ] Risk analysis includes CTO technical considerations
- [ ] Competitive analysis supports CMO positioning strategy

### Quality Gate Testing

**Test Case: Phase Quality Gate Validation**

**Setup Quality Gate Test**:
```python
# test_quality_gates.py
import json
import os

def test_quality_gate_calculation():
    """Test quality gate threshold calculation"""
    phase1_scores = {
        "ceo": 95, "cto": 92, "cfo": 88, "cmo": 90, "coo": 89,
        "chro": 91, "legal": 93, "strategy": 87, "innovation": 94
    }
    
    average_score = sum(phase1_scores.values()) / len(phase1_scores)
    threshold = 95
    
    print(f"Phase 1 Average Score: {average_score:.1f}%")
    print(f"Required Threshold: {threshold}%")
    print(f"Gate Status: {'PASS' if average_score >= threshold else 'FAIL'}")
    
    return average_score >= threshold

if __name__ == "__main__":
    test_quality_gate_calculation()
```

**Validation Checklist**:
- [ ] Quality scores calculated correctly
- [ ] Threshold comparison logic works
- [ ] Gate decision recorded properly
- [ ] Conditional advancement handling
- [ ] User override capabilities tested

## System Testing

### End-to-End Workflow Testing

**Test Case: Complete Workflow Execution**

**Test Scenario**: Execute full 5-phase workflow with test idea

**Phase 1: Executive Evaluation (95% threshold)**
```bash
# Execute all 9 executives sequentially
python eipas.py run-phase 1 --idea "test-workflow-001" --interactive
```

**Expected Results**:
- All 9 executive agents complete successfully
- Average score meets 95% threshold
- Quality gate advances to Phase 2
- Complete artifact chain created

**Phase 2: Business Analysis (90% threshold)**
```bash
# Execute all 4 analysts with Phase 1 context
python eipas.py run-phase 2 --workspace "test-workflow-001" --interactive
```

**Expected Results**:
- All analysts read Phase 1 executive evaluations
- Market and competitive analysis incorporates strategic insights
- Business model aligns with executive recommendations
- Risk assessment includes technical and financial considerations

**Phase 3: Product & Architecture (95% threshold)**
```bash
# Execute all 5 architects with Phase 1-2 context
python eipas.py run-phase 3 --workspace "test-workflow-001" --interactive
```

**Expected Results**:
- Product features align with market analysis
- UX design supports business model requirements
- System architecture meets technical and security requirements
- Data architecture supports analytics and compliance needs

**Phase 4: Implementation (95% threshold, iterative)**
```bash
# Execute implementation with iterative cycles
python eipas.py run-phase 4 --workspace "test-workflow-001" --iterative --max-iterations 3
```

**Expected Results**:
- Each developer produces iteration files
- Frontend implementation matches UX specifications
- Backend services align with system architecture
- DevOps infrastructure supports security requirements

**Phase 5: Quality Assurance (95% threshold, iterative)**
```bash
# Execute QA validation with all previous context
python eipas.py run-phase 5 --workspace "test-workflow-001" --iterative --max-iterations 2
```

**Expected Results**:
- QA strategy covers all implementation components
- Test automation validates functional requirements
- Performance testing meets scalability goals
- Security testing validates compliance requirements

### Performance Testing

**Test Case: System Performance Under Load**

**Load Test Configuration**:
- Concurrent workflows: 5
- Agent execution time: Monitor response times
- File I/O throughput: Measure read/write performance
- Memory usage: Track workspace growth

**Test Script**:
```bash
#!/bin/bash
# performance_test.sh

for i in {1..5}; do
    echo "Starting concurrent workflow $i"
    python eipas.py run "Test Workflow $i Performance Load" --workspace "perf-test-$i" &
done

# Monitor system resources
echo "Monitoring performance..."
top -p $(pgrep -f eipas.py) > performance_metrics.log &
wait
```

**Performance Metrics**:
- [ ] Average agent response time < 30 seconds
- [ ] File I/O operations < 5 seconds per agent
- [ ] Memory usage < 1GB per workflow
- [ ] Concurrent workflow handling without conflicts

## Error Handling Testing

### Failure Scenario Testing

**Test Case: File I/O Failures**
```bash
# Test missing input files
rm workspace/test-workflow-001/phase1/ceo-evaluation.json
python eipas.py run-phase 2 --workspace "test-workflow-001"
# Expected: Graceful error handling with recovery suggestions
```

**Test Case: Quality Gate Failures**
```python
# Simulate low-quality agent outputs
def simulate_quality_failure():
    # Modify agent outputs to have low scores
    phase1_scores = {"ceo": 75, "cto": 80, "cfo": 70}  # Below 95% threshold
    # Test quality gate rejection and improvement recommendations
```

**Test Case: User Interaction Failures**
```bash
# Test invalid user responses
echo "invalid_response" | python eipas.py run "Test Invalid Input"
# Expected: Request clarification and retry input
```

### Recovery Testing

**Test Case: Workflow Resume**
```bash
# Interrupt workflow mid-execution
python eipas.py run "Resume Test Workflow" --workspace "resume-test" &
WORKFLOW_PID=$!
sleep 30
kill -INT $WORKFLOW_PID

# Resume workflow
python eipas.py resume "resume-test"
# Expected: Successful continuation from interruption point
```

## User Acceptance Testing

### Interactive Collaboration Testing

**Test Case: User Approval Gates**
1. Start workflow with complex business idea
2. Verify each agent presents evaluation criteria clearly
3. Test user input acceptance and validation
4. Confirm approval gates function correctly
5. Validate user feedback integration

**Test Case: Iterative Development Testing**
1. Execute Phase 4 implementation agents
2. Test multiple iteration cycles
3. Verify user feedback incorporation between iterations
4. Confirm iterative improvement tracking

### Usability Testing

**Test Scenarios**:
1. **New User Experience**: First-time system usage
2. **Complex Workflow**: Multi-phase execution with dependencies
3. **Error Recovery**: Handling failures and resuming workflows
4. **Quality Override**: Manual threshold overrides with justification

## Automated Testing Framework

### Test Automation Script

```python
#!/usr/bin/env python3
# automated_test_suite.py

import json
import os
import subprocess
import sys
from pathlib import Path

class EIPASTestSuite:
    def __init__(self):
        self.test_workspace = "automated-test-001"
        self.results = {"passed": 0, "failed": 0, "errors": []}
    
    def setup_test_environment(self):
        """Initialize test environment"""
        subprocess.run(["python", "eipas.py", "init"], check=True)
        
    def test_agent_file_io(self, agent_path, phase):
        """Test individual agent file I/O operations"""
        try:
            # Execute agent and validate output
            result = subprocess.run([
                "claude-code", "--template", agent_path,
                "--workspace", f"workspace/{self.test_workspace}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.results["passed"] += 1
                return True
            else:
                self.results["failed"] += 1
                self.results["errors"].append(f"Agent {agent_path} failed: {result.stderr}")
                return False
        except Exception as e:
            self.results["failed"] += 1
            self.results["errors"].append(f"Exception testing {agent_path}: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Execute complete test suite"""
        print("Starting EIPAS Comprehensive Test Suite...")
        
        # Test all agents
        agent_templates = Path("installer/agent-templates")
        for phase_dir in agent_templates.iterdir():
            if phase_dir.is_dir():
                for agent_file in phase_dir.glob("*.md"):
                    print(f"Testing {agent_file.name}...")
                    self.test_agent_file_io(str(agent_file), phase_dir.name)
        
        # Print results
        print(f"\nTest Results:")
        print(f"Passed: {self.results['passed']}")
        print(f"Failed: {self.results['failed']}")
        
        if self.results["errors"]:
            print("\nErrors:")
            for error in self.results["errors"]:
                print(f"  - {error}")
        
        return self.results["failed"] == 0

if __name__ == "__main__":
    test_suite = EIPASTestSuite()
    success = test_suite.run_comprehensive_test()
    sys.exit(0 if success else 1)
```

## Testing Checklist

### Pre-Release Validation
- [ ] All 32 agents execute successfully with test data
- [ ] Cross-phase file I/O operations work correctly
- [ ] Quality gates enforce thresholds properly
- [ ] Interactive collaboration functions as expected
- [ ] Error handling provides helpful recovery guidance
- [ ] Performance meets acceptable thresholds
- [ ] Documentation is complete and accurate

### Release Criteria
- [ ] 100% agent compatibility with Claude Code
- [ ] Complete workflow execution without critical errors
- [ ] User acceptance testing passes all scenarios
- [ ] Performance benchmarks meet requirements
- [ ] Security validation passes all checks
- [ ] Cross-platform compatibility verified

This comprehensive testing framework ensures the EIPAS system delivers reliable, high-quality workflow automation with full Claude Code integration and collaborative user engagement.