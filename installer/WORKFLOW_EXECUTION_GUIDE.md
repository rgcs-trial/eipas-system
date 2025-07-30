# EIPAS Workflow Execution Guide

## Overview

The Enterprise Idea-to-Product Automation System (EIPAS) is a comprehensive 5-phase workflow that transforms business ideas into production-ready implementations through collaborative Claude agent interactions.

## System Architecture

### Core Components
- **32 Specialized Agents** across 5 phases + meta management
- **Interactive Mode**: All agents require user approval and collaboration
- **File-Based Continuity**: Cross-phase workflow through persistent JSON artifacts
- **Quality Gates**: Threshold validation between phases (90-95% requirements)
- **Iterative Support**: Phases 4-5 support multiple development iterations

### Workspace Structure
```
~/.claude/eipas-system/workspace/[workflow-id]/
├── idea.json                           # Initial business concept
├── workflow-status.json                # Progress tracking
├── phase1/                            # Executive Evaluations (9 agents)
│   ├── ceo-evaluation.json
│   ├── cto-evaluation.json
│   ├── cfo-evaluation.json
│   └── ... (6 more executives)
├── phase2/                            # Business Analysis (4 agents)
│   ├── market-analyst.json
│   ├── business-analyst.json
│   ├── competitive-analyst.json
│   └── risk-analyst.json
├── phase3/                            # Product & Architecture (5 agents)
│   ├── product-manager-evaluation.json
│   ├── ux-designer-evaluation.json
│   ├── system-architect-evaluation.json
│   ├── data-architect.json
│   └── security-architect.json
├── phase4/                            # Implementation (4 agents, iterative)
│   ├── senior-developer-iteration-*.json
│   ├── frontend-developer-iteration-*.json
│   ├── backend-developer-iteration-*.json
│   └── devops-engineer-iteration-*.json
├── phase5/                            # Quality Assurance (4 agents, iterative)
│   ├── qa-lead-iteration-*.json
│   ├── test-automation-iteration-*.json
│   ├── performance-tester-iteration-*.json
│   └── security-tester-iteration-*.json
└── quality-gates/                     # Meta agent decisions
    ├── phase-1-gate-decision.json
    ├── phase-2-gate-decision.json
    └── ... (quality gate decisions)
```

## Phase-by-Phase Execution Guide

### Phase 1: Executive Evaluation (95% Threshold)
**Objective**: C-suite assessment of strategic fit, feasibility, and investment potential

**Agents (Sequential Execution)**:
1. **CEO** - Strategic alignment and business case validation
2. **CTO** - Technical feasibility and architecture requirements
3. **CFO** - Financial viability and investment analysis
4. **CMO** - Market positioning and go-to-market strategy
5. **COO** - Operational feasibility and resource requirements
6. **CHRO** - Human resources and team building needs
7. **Legal Counsel** - Regulatory compliance and legal structure
8. **VP Strategy** - Portfolio alignment and strategic synergies
9. **Innovation Director** - Innovation potential and competitive advantage

**User Collaboration**:
- Each agent presents evaluation criteria and asks clarifying questions
- User provides business context, constraints, and strategic priorities
- Explicit approval required: "Execute [Agent] evaluation with your input? (y/n)"

**Quality Gate**: 95% threshold required to advance to Phase 2

### Phase 2: Business Analysis (90% Threshold)
**Objective**: Deep market analysis, competitive landscape, and business model validation

**Agents (Parallel Execution Possible)**:
1. **Market Analyst** - Market size, trends, and opportunity analysis
2. **Business Analyst** - Business model design and revenue projections
3. **Competitive Analyst** - Competitive landscape and differentiation strategy
4. **Risk Analyst** - Risk assessment and mitigation strategies

**Cross-Phase Integration**:
- All agents read Phase 1 executive evaluations
- Build on CEO strategic direction, CTO technical insights, CFO financial constraints

**User Collaboration**:
- Market research validation and customer insight sharing
- Business model assumptions and revenue expectations
- Competitive intelligence and positioning preferences

### Phase 3: Product & Architecture (95% Threshold)
**Objective**: Product definition, user experience design, and technical architecture

**Agents (Mixed Sequential/Parallel)**:
1. **Product Manager** - Feature prioritization and product roadmap
2. **UX Designer** - User experience design and interface planning
3. **System Architect** - Technical architecture and integration strategy
4. **Data Architect** - Data models and analytics framework
5. **Security Architect** - Security architecture and compliance framework

**Cross-Phase Integration**:
- Reads all Phase 1-2 outputs for comprehensive context
- Product features align with market analysis and executive priorities
- Architecture supports business model and operational requirements

### Phase 4: Implementation (95% Threshold, Iterative)
**Objective**: Development implementation with iterative improvement cycles

**Agents (Iterative Execution)**:
1. **Senior Developer** - Core business logic and application architecture
2. **Frontend Developer** - User interface and user experience implementation
3. **Backend Developer** - API design and server-side implementation
4. **DevOps Engineer** - Infrastructure, deployment, and operational setup

**Iterative Process**:
- Each agent produces iteration files: `*-iteration-{N}.json`
- Multiple development cycles with user approval gates
- Continuous integration with previous phase specifications

### Phase 5: Quality Assurance (95% Threshold, Iterative)
**Objective**: Comprehensive testing and quality validation

**Agents (Iterative Execution)**:
1. **QA Lead** - Test strategy and quality planning
2. **Test Automation** - Automated testing framework and coverage
3. **Performance Tester** - Load testing and performance optimization
4. **Security Tester** - Security validation and vulnerability assessment

**Quality Validation**:
- Each agent validates implementation against all previous phase requirements
- Iterative testing cycles with improvement feedback
- Final release readiness assessment

## User Interaction Patterns

### Standard Agent Interaction Flow
```
🎯 [AGENT NAME] EVALUATION

📋 "I'll evaluate from a [perspective]. Here's what I need to assess:
   • [Evaluation criteria 1]
   • [Evaluation criteria 2]
   • [Evaluation criteria 3]

🤔 Before I begin, help me understand:
   • [Clarifying question 1]
   • [Clarifying question 2]
   • [Clarifying question 3]

📊 Based on your input, here's my assessment:
   [Present detailed analysis and recommendations]

🚪 [Agent] Recommendation: [Decision with reasoning]
   
   [Approval question specific to next steps]"
```

### Quality Gate Interactions
- Present phase completion scores and threshold analysis
- Explain quality gaps and improvement recommendations
- Request explicit approval: "Phase N completed with X% quality. Proceed to Phase N+1? (y/n)"
- Offer conditional advancement with improvement conditions

## File I/O Integration

### Reading Pattern
Each agent reads relevant previous phase outputs:
```json
"input_references": [
  "workspace/phase1/ceo-evaluation.json",
  "workspace/phase2/market-analyst.json",
  "workspace/phase3/product-manager-evaluation.json",
  "workspace/idea.json"
]
```

### Writing Pattern
Each agent writes structured output:
```json
{
  "agent": "agent-name",
  "phase": "phase-number",
  "timestamp": "ISO-8601-timestamp",
  "evaluation": { /* agent-specific scores */ },
  "analysis": { /* detailed assessment */ },
  "recommendation": "GO/NO-GO with reasoning",
  "cross_phase_synthesis": { /* integration insights */ }
}
```

## Quality Thresholds

| Phase | Threshold | Agents | Focus Area |
|-------|-----------|--------|------------|
| Phase 1 | 95% | 9 Executives | Strategic Validation |
| Phase 2 | 90% | 4 Analysts | Market Validation |
| Phase 3 | 95% | 5 Architects | Design Validation |
| Phase 4 | 95% | 4 Developers | Implementation Quality |
| Phase 5 | 95% | 4 QA Specialists | Release Readiness |

## Execution Commands

### System Initialization
```bash
python eipas.py init        # Initialize EIPAS system
python eipas.py health      # Validate system configuration
```

### Workflow Execution
```bash
python eipas.py run "Your business idea"    # Start workflow
python eipas.py status                      # Check progress
python eipas.py resume [workflow-id]        # Resume workflow
```

### Workflow Management
```bash
python eipas.py list                        # List all workflows
python eipas.py export [workflow-id]        # Export results
python eipas.py cleanup [workflow-id]       # Clean workspace
```

## Success Criteria

### Workflow Completion
- All 5 phases completed with threshold scores
- Complete artifact chain from idea to implementation
- Quality gates passed with user approval
- Final deliverables include:
  - Business case and strategic alignment
  - Market validation and competitive analysis
  - Product specification and architecture design
  - Implementation code and infrastructure
  - Quality validation and testing results

### Quality Metrics
- Cross-phase consistency and alignment
- Decision traceability through artifact chain
- User approval and satisfaction ratings
- Implementation readiness for production deployment

## Troubleshooting

### Common Issues
1. **Quality Gate Failures**: Review agent scores, implement improvement recommendations
2. **File I/O Errors**: Ensure workspace permissions and directory structure
3. **Agent Interaction Issues**: Validate user input and approval responses
4. **Cross-Phase Inconsistencies**: Review previous phase outputs for alignment

### Recovery Procedures
- Workflow resume capability with state restoration
- Agent re-execution with improved inputs
- Quality gate override with user justification
- Partial workflow completion with milestone achievements

This comprehensive guide enables effective execution of the EIPAS workflow with full Claude Code compliance and collaborative user engagement throughout the entire idea-to-product automation process.