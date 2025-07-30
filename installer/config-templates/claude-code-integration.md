# EIPAS Claude Code Integration Guide

## Overview
The EIPAS system has been architected specifically for Claude Code's interactive, user-approval-based model rather than autonomous multi-agent execution.

## Key Architectural Principles

### 1. Interactive Mode (Not Autonomous)
- **Guided Workflow**: Agents act as interactive guides that present options and await user approval
- **User Control**: Every agent execution requires explicit user confirmation
- **Collaborative Process**: Agents ask clarifying questions and work with users to refine outputs

### 2. User Approval Gates
- **Phase Gates**: Explicit user confirmation required before advancing between phases
- **Agent Execution**: "Execute [Agent Name] for [Task]? (y/n)" pattern
- **Quality Reviews**: Present results and ask for user approval to proceed
- **Iteration Control**: User decides whether to continue iterations or advance

### 3. Simplified Orchestration
- **Single-Agent Focus**: Each agent execution is independent with user approval
- **No Background Processing**: All activity happens in foreground with user visibility
- **Claude Code Native**: Leverages existing Claude Code capabilities for file editing, command execution

## Implementation Strategy

### Phase Execution Pattern
```
1. Phase Overview: Present objectives and available agents
2. Agent Selection: User chooses which agents to execute
3. Agent Execution: Single agent runs with user monitoring
4. Results Review: Present output and quality assessment
5. User Decision: Continue in phase, advance, or iterate
```

### Agent Interaction Model
```
🎯 AGENT INTRODUCTION
Present role and evaluation criteria

🤔 COLLABORATIVE INPUT  
Ask clarifying questions specific to the idea

📊 INTERACTIVE ANALYSIS
Work with user to evaluate each criterion

🚪 RECOMMENDATION & APPROVAL
Present findings and await user decision
```

### Quality Gate Management
- **Threshold Guidance**: Explain what each threshold means
- **Score Presentation**: Show detailed scoring breakdown
- **User Override**: Allow user to proceed even if threshold not met (with warnings)
- **Iteration Opportunities**: Offer to refine and retry if scores are low

## Compliance Features

### User Approval Requirements
- Every agent execution requires explicit user confirmation
- Phase transitions need user approval
- Quality gate advancement is user-controlled
- Iteration cycles are user-initiated

### Interactive Workflows
- Agents present information and await user input
- Collaborative analysis with user participation
- Results review with user feedback opportunities
- Guided decision-making with clear recommendations

### Claude Code Integration
- Compatible with existing slash command system
- Works with Claude Code's file editing capabilities
- Integrates with task management and progress tracking
- Supports resume functionality through state persistence

## Usage Examples

### Starting a Workflow
```
User: /eipas
System: Welcome to EIPAS Interactive Workflow Guide. Let's start with your innovative idea...

User: [Provides idea]
System: Great! I'll guide you through 5 phases. Ready to begin Phase 1 - CXO Evaluation?

User: Yes
System: Phase 1 has 9 executive agents. Should I start with the CEO evaluation? (y/n)
```

### Agent Execution
```
System: 🎯 CEO STRATEGIC EVALUATION
I'll evaluate your idea from a CEO perspective. Before I begin, can you help me understand:
• What's your target market size?
• Who are your main competitors?
• How do you plan to monetize this?

User: [Provides answers]
System: Based on your input, here's my assessment... [detailed analysis]
CEO Recommendation: GO (Score: 92/100)
Proceed to CTO evaluation? (y/n)
```

This approach ensures full compliance with Claude Code's interactive model while maintaining the comprehensive workflow capabilities of the EIPAS system.