# File I/O Pattern for EIPAS Agents

## Standard File I/O Pattern to Add to All Agents

Add this section before the final "Execute interactive..." line in each agent:

```markdown
## File I/O Operations
- **Read Input**: Review relevant previous phase outputs from .claude-agentflow/workspace/
  - **Phase 1**: `.claude-agentflow/workspace/phase1/` - Executive strategic evaluations
  - **Phase 2**: `.claude-agentflow/workspace/phase2/` - Business analysis and market insights  
  - **Phase 3**: `.claude-agentflow/workspace/phase3/` - Product strategy and architecture
  - **Phase 4**: `.claude-agentflow/workspace/phase4/` - Implementation progress and code artifacts
- **Write Output**: Create `.claude-agentflow/workspace/phase{N}/{agent-name}.json` with evaluation results
- **Reference Files**: Cross-phase synthesis of all relevant workflow context

## Output File Structure
```json
{
  "agent": "{agent-name}",
  "phase": "phase{N}",
  "timestamp": "2024-01-01T12:00:00Z",
  "input_references": [
    ".claude-agentflow/workspace/idea.json",
    ".claude-agentflow/workspace/phase{N-1}/{relevant-agent}.json"
  ],
  "evaluation": {
    "{agent}_score": 85,
    "key_metrics": {
      "metric1": 90,
      "metric2": 80,
      "metric3": 85
    }
  },
  "key_strengths": ["Strength 1", "Strength 2", "Strength 3"],
  "areas_for_improvement": ["Improvement 1", "Improvement 2", "Improvement 3"],
  "recommendation": "PROCEED/CONDITIONAL/STOP with reasoning",
  "next_steps": ["Action 1", "Action 2", "Action 3"],
  "cross_phase_insights": {
    "previous_phase_alignment": "How this evaluation builds on previous phases",
    "workflow_continuity": "Key insights carried forward from earlier evaluations"
  }
}
```

## Phase-Specific Input Patterns

### Phase 1 Agents (Executives)
- **Read**: `.claude-agentflow/workspace/idea.json` (initial business concept)
- **Write**: `.claude-agentflow/workspace/phase1/{agent-name}-evaluation.json`

### Phase 2 Agents (Business Analysis)  
- **Read**: All `.claude-agentflow/workspace/phase1/*.json` files for strategic context
- **Write**: `.claude-agentflow/workspace/phase2/{agent-name}.json`

### Phase 3 Agents (Architecture)
- **Read**: `.claude-agentflow/workspace/phase1/` and `.claude-agentflow/workspace/phase2/` for requirements
- **Write**: `.claude-agentflow/workspace/phase3/{agent-name}.json`

### Phase 4 Agents (Implementation)
- **Read**: `.claude-agentflow/workspace/phase1/`, `phase2/`, `phase3/` for complete context
- **Write**: `.claude-agentflow/workspace/phase4/{agent-name}-iteration-{N}.json` (iterative)

### Phase 5 Agents (QA)
- **Read**: All previous phases plus Phase 4 implementation artifacts
- **Write**: `.claude-agentflow/workspace/phase5/{agent-name}-iteration-{N}.json` (iterative)

### Meta Agents
- **Read**: All relevant phase outputs based on agent scope
- **Write**: `.claude-agentflow/workspace/meta/{agent-name}-analysis.json`
```

## Instructions for Implementation

1. Add the File I/O Operations section to each agent
2. Customize the input_references array for each agent's specific needs
3. Adjust the evaluation metrics based on the agent's expertise
4. Ensure cross_phase_insights reflect the agent's unique perspective
5. Update the final execution line to mention file-based continuity

## Benefits

- **Workflow Continuity**: Each agent builds on previous insights
- **Decision Traceability**: Full audit trail from idea to implementation  
- **Context Preservation**: No information loss between phases
- **Collaborative Intelligence**: Agents work together through shared artifacts
- **Resume Capability**: Workflows can be paused and resumed with full context