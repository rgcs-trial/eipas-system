# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### System Initialization
```bash
python eipas.py init        # Initialize EIPAS system directories and configuration
python eipas.py health      # Check system health and configuration
```

### Running Workflows
```bash
python eipas.py run "Your innovative idea"  # Execute complete workflow
python eipas.py status                      # Check workflow status and results
```

### System Maintenance
```bash
# No external dependencies required - uses Python standard library only
python eipas.py health      # Validate system configuration
```

## Architecture Overview

EIPAS is a simulation of an Enterprise Idea-to-Product Automation System that processes ideas through 5 sequential phases with quality gates:

### Core Architecture
- **Phase-based workflow**: Ideas progress through CXO → Business → Product → Implementation → QA phases
- **Quality gates**: Each phase must meet threshold scores (90-95%) to proceed
- **Agent simulation**: 29 specialized AI agents (currently simulated, designed for Claude integration)
- **Workspace management**: Each workflow creates isolated workspace in `~/.claude/eipas-system/workspace/`

### Key Components

**Main Class**: `EIPAS` (eipas.py:16-321)
- Manages workflow orchestration
- Handles phase execution and quality gates
- Provides CLI interface and status monitoring

**Phase Structure**:
1. **Phase 1 - CXO Evaluation**: 9 executives (CEO, CTO, CFO, etc.) - 95% threshold
2. **Phase 2 - Business Analysis**: 4 analysts - 90% threshold  
3. **Phase 3 - Product & Architecture**: 5 specialists - 95% threshold
4. **Phase 4 - Implementation**: 4 developers - 95% threshold
5. **Phase 5 - Quality Assurance**: 4 QA specialists - 95% threshold

**Workspace Structure**: `~/.claude/eipas-system/`
```
├── config/eipas-config.json    # System configuration
├── agent-prompts/              # Agent prompt templates (future Claude integration)
└── workspace/                  # Individual workflow results
    └── eipas-[timestamp]-[idea-slug]/
        ├── idea.json           # Workflow metadata and results
        ├── phase1/             # Phase outputs
        ├── phase2/
        └── ...
```

## Development Notes

- **Current State**: Simulation system with randomized agent scores
- **Future Integration**: Designed for Claude API integration replacing `_simulate_agent()` method
- **Quality Gates**: Configurable thresholds in `quality_gates` dict (eipas.py:24-30)
- **Agent Execution**: Sequential phases, with parallel/sequential agent execution per phase
- **Error Handling**: Workflow fails if critical phase quality gates not met

## Configuration

System settings stored in `~/.claude/eipas-system/config/eipas-config.json`:
- Quality gate thresholds for each phase
- Agent definitions and execution parameters
- Phase configuration (parallel/sequential, timeouts)

The system is self-contained with no external dependencies beyond Python standard library.