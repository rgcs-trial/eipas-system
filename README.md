# claudeAgentFlow - Claude Agent Workflow Automation System

![claudeAgentFlow Logo](https://img.shields.io/badge/claudeAgentFlow-Workflow%20Automation-blue?style=for-the-badge)
![Claude Code](https://img.shields.io/badge/Claude%20Code-Integrated-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)

## 🚀 Overview

**claudeAgentFlow** is a revolutionary workflow automation platform that transforms business ideas into production-ready implementations through intelligent Claude agent orchestration. The system guides users through a comprehensive 5-phase process with 32 specialized agents, ensuring thorough evaluation, design, implementation, and quality assurance.

### 🆕 Recent Major Updates
- **Project Rename**: Complete transformation from EIPAS to claudeAgentFlow
- **Consolidated Architecture**: All system files now organized in `.claude-agentflow/` directory
- **GitHub Repository**: Renamed to `claude-agentflow` with updated remote references
- **Claude Code Compliance**: Full integration with Claude Code CLI standards
- **Enhanced File Structure**: Streamlined organization with proper template separation

## ✨ Key Features

### 🤖 **32 Specialized Claude Agents**
- **Phase 1**: 9 Executive Agents (CEO, CTO, CFO, CMO, COO, CHRO, Legal, Strategy VP, Innovation Director)
- **Phase 2**: 4 Business Analysis Agents (Market, Business, Competitive, Risk Analysts)
- **Phase 3**: 5 Product & Architecture Agents (Product Manager, UX Designer, System/Data/Security Architects)
- **Phase 4**: 4 Implementation Agents (Senior/Frontend/Backend Developers, DevOps Engineer)
- **Phase 5**: 4 Quality Assurance Agents (QA Lead, Test Automation, Performance/Security Testers)
- **Meta**: 6 Orchestration Agents (Workflow management and quality gates)

### 🔄 **Interactive Collaboration**
- **User Approval Gates**: Every agent requires explicit user confirmation
- **Collaborative Input**: Agents ask clarifying questions and incorporate user feedback
- **Context-Aware Processing**: Each agent builds on previous phase insights
- **Iterative Development**: Phases 4-5 support multiple improvement cycles

### 📁 **Cross-Phase Workflow Continuity**
- **File-Based Integration**: Structured JSON artifacts enable seamless information flow
- **Decision Traceability**: Complete audit trail from initial idea to final implementation
- **Context Preservation**: No loss of insights between phases
- **Quality Gates**: Configurable thresholds (90-95%) ensure advancement readiness

### 🎯 **Enterprise-Grade Quality**
- **Quality Thresholds**: Phase-specific scoring requirements with override capabilities
- **Comprehensive Testing**: Automated validation and performance benchmarking
- **Security First**: Built-in security validation and compliance frameworks
- **Scalable Architecture**: Support for concurrent workflows and enterprise deployment

## 📋 Prerequisites

- **Python 3.8+** with standard library
- **Claude Code CLI** installed and authenticated
- **Minimum 1GB** available disk space
- **Read/write permissions** for `~/.claude` directory

## 🛠️ Quick Installation

### 1. Clone and Install
```bash
git clone https://github.com/rgcs-trial/claude-agentflow.git claude-agentflow
cd claude-agentflow
python install-eipas.py
```

### 2. Verify Installation
```bash
python install-eipas.py --validate
```

### 3. Initialize System
```bash
python main.py init
python main.py health
```

## 🚀 Quick Start

### Basic Workflow Execution
```bash
# Start a new workflow
python main.py run "AI-powered customer service automation platform"

# Check workflow status
python main.py status

# Resume interrupted workflow
python main.py resume [workflow-id]
```

### Interactive Agent Execution
```bash
# Execute specific agent with Claude Code
claude-code --template agent-templates/phase1/ceo.md

# Run complete phase
python main.py run-phase 1 --interactive
```

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     claudeAgentFlow System Architecture                   │
├─────────────────────────────────────────────────────────────────┤
│  User Interface Layer: Claude Code CLI + Interactive Prompts   │
├─────────────────────────────────────────────────────────────────┤
│  Orchestration Layer: Workflow Engine + Quality Gates          │
├─────────────────────────────────────────────────────────────────┤
│  Agent Execution Layer: 32 Specialized Claude Agents           │
├─────────────────────────────────────────────────────────────────┤
│  Data Persistence Layer: JSON Artifacts + Cross-Phase I/O      │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow Structure
```
{workspace-name}/
├── .claude/                     # Claude Code configuration
│   ├── settings.json           # Hooks and environment variables
│   ├── agents/                 # 32 specialized agent templates
│   └── commands/               # claudeAgentFlow CLI commands
└── .claude-agentflow/          # Consolidated claudeAgentFlow system
    ├── config/                 # System configuration
    ├── hooks/                  # Hook scripts
    ├── database/
    │   └── memory.db           # SQLite database
    └── workspace/              # Active workflow artifacts
        ├── idea.json           # Initial business concept
        ├── workflow-status.json # Progress tracking
        ├── phase1/             # Executive evaluations (9 files)
        ├── phase2/             # Business analysis (4 files)
        ├── phase3/             # Product & architecture (5 files)
        ├── phase4/             # Implementation iterations
        └── phase5/             # QA validation iterations
```

## 🎮 User Experience

### Agent Interaction Pattern
```
🎯 [AGENT NAME] EVALUATION

📋 "I'll evaluate from a [perspective]. Here's what I need to assess:
   • [Evaluation criteria 1]
   • [Evaluation criteria 2]
   • [Evaluation criteria 3]

🤔 Before I begin, help me understand:
   • [Clarifying question 1]
   • [Clarifying question 2]

📊 Based on your input, here's my assessment:
   [Detailed analysis and recommendations]

🚪 [Agent] Recommendation: [Decision with reasoning]
   
   Ready to proceed? (y/n)"
```

### Quality Gates
- **Phase 1**: 95% threshold (Strategic validation)
- **Phase 2**: 90% threshold (Market validation)
- **Phase 3**: 95% threshold (Design validation)
- **Phase 4**: 95% threshold (Implementation quality)
- **Phase 5**: 95% threshold (Release readiness)

## 📚 Documentation

### Core Documentation
- **[Workflow Execution Guide](WORKFLOW_EXECUTION_GUIDE.md)** - Complete workflow execution instructions
- **[System Architecture Overview](SYSTEM_ARCHITECTURE_OVERVIEW.md)** - Technical architecture and integration
- **[Testing Documentation](TESTING_DOCUMENTATION.md)** - Comprehensive testing procedures
- **[System Validation](SYSTEM_VALIDATION.md)** - Validation and health check procedures

### Agent Templates
- **[Phase 1 Executives](agent-templates/phase1/)** - C-suite strategic evaluation
- **[Phase 2 Analysts](agent-templates/phase2/)** - Business and market analysis
- **[Phase 3 Architects](agent-templates/phase3/)** - Product and technical design
- **[Phase 4 Developers](agent-templates/phase4/)** - Implementation and infrastructure
- **[Phase 5 QA Specialists](agent-templates/phase5/)** - Quality assurance and testing
- **[Meta Agents](agent-templates/meta/)** - Workflow orchestration and management

## 🧪 Testing and Validation

### Quick Validation
```bash
# System health check
python main.py health

# Run test workflow
python utils/system_health_check.py --quick

# Validate agent templates
python core/validator.py --agents
```

### Comprehensive Testing
```bash
# Full system test suite
python utils/system_health_check.py --comprehensive

# Performance benchmarking
python core/installer.py --benchmark

# Security validation  
python core/validator.py --security
```

## 🔧 Configuration

### System Configuration
- **Quality Thresholds**: `config-templates/quality-gates.json`
- **Workflow Settings**: `config-templates/workflow-settings.json`
- **Agent Behavior**: `config-templates/agent-behavior.json`

### Claude Code Integration
- **Settings**: `.claude/settings.json` (hooks and environment variables)
- **Agent Templates**: `agent-templates/` (32 specialized agents)
- **Commands**: `command-templates/` (claudeAgentFlow CLI interface)
- **System Files**: `.claude-agentflow/` (hooks, database, workspace)

## 🚨 Troubleshooting

### Common Issues
1. **Agent Template Loading**: Check Claude Code CLI authentication
2. **File I/O Errors**: Verify workspace permissions
3. **Quality Gate Failures**: Review agent scores and thresholds
4. **Cross-Phase Dependencies**: Validate previous phase completions

### Diagnostic Tools
```bash
# Generate diagnostic report
python utils/system_health_check.py --diagnostic

# Export system logs
python core/database.py --export-logs

# System repair utility
python core/installer.py --repair
```

## 🔐 Security

### Data Protection
- **Workspace Isolation**: Each workflow runs in isolated directory
- **Secure Configuration**: Encrypted storage of sensitive settings
- **Audit Trail**: Complete logging of all user interactions and decisions
- **Access Control**: File permission management and user authentication

### Compliance
- **Data Privacy**: GDPR/CCPA compliant data handling
- **Security Standards**: SOC 2 Type II compatible controls
- **Enterprise Security**: Role-based access and audit logging

## 🚀 Performance

### Benchmarks
- **Agent Execution**: < 30 seconds per agent
- **File I/O Operations**: < 5 seconds per operation
- **Memory Usage**: < 500MB per workflow
- **Concurrent Workflows**: 5+ simultaneous executions supported

### Scalability
- **Horizontal Scaling**: Multiple concurrent workflow support
- **Resource Optimization**: Efficient memory and disk usage
- **Cloud Deployment**: Container-ready architecture
- **Load Balancing**: Distributed agent execution capabilities

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone https://github.com/rgcs-trial/claude-agentflow.git claude-agentflow-dev
cd claude-agentflow-dev

# Install development dependencies
pip install -r requirements-dev.txt

# Run development test suite
python -m pytest tests/
```

### Adding New Agents
1. Create agent template in appropriate phase directory
2. Follow [File I/O Pattern](agent-templates/FILE_IO_PATTERN.md)
3. Add interactive mode with user approval gates
4. Include comprehensive testing and validation

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Anthropic** for Claude Code platform integration
- **Enterprise Development Community** for workflow automation insights
- **Open Source Contributors** for continuous improvement and feedback

## 📞 Support

### Community Support
- **Documentation**: Complete guides and API references
- **Issues**: GitHub issue tracker for bug reports and feature requests
- **Discussions**: Community forum for questions and best practices

### Enterprise Support
- **Professional Services**: Implementation and customization assistance
- **Training Programs**: User and administrator training
- **24/7 Support**: Enterprise-grade support and maintenance

---

**claudeAgentFlow - Transforming Ideas into Products through Intelligent Automation**

*Built with ❤️ for enterprise innovation and powered by Claude Code*