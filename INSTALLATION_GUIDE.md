# Claude Code Configuration Installer - Installation Guide

## Overview

The Claude Code Configuration Installer is an intelligent system that automatically detects your project's technology stack and generates optimized Claude Code configurations including agents, hooks, and commands tailored to your specific development workflow.

## Prerequisites

- **Claude Code**: Must be installed and accessible via command line
- **Python 3.8+**: Required for running the installer
- **Git**: Recommended for backup and version control features
- **Project Access**: Read/write permissions to your project directory or user home directory

## Quick Start

### 1. Download the Installer

```bash
git clone <repository-url>
cd claude-config-installer
```

### 2. Run the Installer

```bash
python claude-config-installer.py
```

### 3. Choose Installation Scope

The installer will prompt you to choose:
- **Project Level**: Configurations shared with your team (`.claude/` in project root)
- **User Level**: Personal configurations across all projects (`~/.claude/`)

### 4. Follow Interactive Setup

The installer will:
1. Analyze your project structure
2. Detect existing development tools
3. Recommend optimal configuration profile
4. Generate and install customized configurations

## Installation Profiles

### Web Frontend (`web-frontend`)
**Best for**: React, Vue, Angular, Next.js projects

**Includes**:
- **Agents**: Component reviewer, accessibility checker, performance optimizer
- **Hooks**: Auto-format with Prettier, ESLint validation, test runner
- **Commands**: `/build`, `/test`, `/deploy`, `/format`

**Auto-detected from**:
- `package.json` with React/Vue/Angular dependencies
- Presence of `webpack.config.js`, `vite.config.js`
- TypeScript configurations

### Backend API (`backend-api`)
**Best for**: Express.js, Django, FastAPI, Spring Boot projects

**Includes**:
- **Agents**: API reviewer, security auditor, database schema validator
- **Hooks**: Auto-format, linting, unit test execution
- **Commands**: `/api-test`, `/migrate`, `/security-scan`

**Auto-detected from**:
- `package.json` with Express dependencies
- `requirements.txt` with Django/FastAPI
- `pom.xml` or `build.gradle` files

### Data Science (`data-science`)
**Best for**: Jupyter notebooks, ML projects, data analysis

**Includes**:
- **Agents**: Data validator, model reviewer, notebook optimizer
- **Hooks**: Notebook cleanup, dependency checks
- **Commands**: `/analyze`, `/train`, `/validate-data`

**Auto-detected from**:
- `requirements.txt` with pandas/numpy/scikit-learn
- Presence of `.ipynb` files
- `pyproject.toml` with data science dependencies

### DevOps (`devops`)
**Best for**: Infrastructure, deployment, CI/CD projects

**Includes**:
- **Agents**: Infrastructure reviewer, security scanner, deployment validator
- **Hooks**: Terraform validation, Docker builds
- **Commands**: `/deploy`, `/infra-check`, `/security-audit`

**Auto-detected from**:
- Presence of `Dockerfile`, `docker-compose.yml`
- Terraform files (`.tf`)
- Kubernetes manifests (`*.yaml` in k8s directories)

### Enterprise (`enterprise`)
**Best for**: Corporate environments with strict compliance

**Includes**:
- **Agents**: Compliance checker, security auditor, code quality enforcer
- **Hooks**: Security scans, license validation, audit logging
- **Commands**: `/compliance-check`, `/security-report`, `/audit`

**Features**:
- Enhanced security permissions
- Audit trail logging
- Policy enforcement
- Integration with enterprise tools

## Manual Configuration

### Custom Installation

```bash
python claude-config-installer.py --profile custom
```

This allows you to:
- Select specific agents to install
- Choose which hooks to enable
- Customize command configurations
- Set granular permissions

### Advanced Options

```bash
# Install to specific directory
python claude-config-installer.py --path /path/to/project

# Backup existing configs
python claude-config-installer.py --backup

# Merge with existing configurations
python claude-config-installer.py --merge

# Dry run (preview changes)
python claude-config-installer.py --dry-run
```

## Configuration Structure

After installation, your configurations will be organized as:

### Project Level (`.claude/`)
```
.claude/
├── settings.json              # Main configuration
├── settings.local.json        # Personal overrides (gitignored)
├── agents/                    # Custom agents
│   ├── code-reviewer.md
│   ├── test-generator.md
│   └── security-auditor.md
├── commands/                  # Slash commands
│   ├── test.md
│   ├── build.md
│   └── deploy.md
└── hooks/                     # Hook scripts
    ├── format-code.sh
    ├── run-tests.sh
    └── security-check.sh
```

### User Level (`~/.claude/`)
```
~/.claude/
├── settings.json              # Global configuration
├── agents/                    # Personal agents
├── commands/                  # Personal commands
└── backups/                   # Configuration backups
    └── 2025-07-30-backup/
```

## Example Configurations

### React + TypeScript Project

**Generated Agent** (`.claude/agents/react-reviewer.md`):
```markdown
---
name: React Component Reviewer
description: Reviews React components for best practices
---

Review this React component for:
- TypeScript usage and type safety
- React hooks best practices
- Performance optimizations
- Accessibility compliance
- Component composition patterns
```

**Generated Hook** (`.claude/settings.json`):
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit.*\\.(tsx?|jsx?)$",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write $CLAUDE_MODIFIED_FILES"
          },
          {
            "type": "command", 
            "command": "npx eslint $CLAUDE_MODIFIED_FILES --fix"
          }
        ]
      }
    ]
  }
}
```

### Python Django Project

**Generated Command** (`.claude/commands/test.md`):
```markdown
---
description: Run Django tests with coverage
---

Run the Django test suite:

```bash
python manage.py test --coverage
```

Ensure all tests pass before committing changes.
```

## Troubleshooting

### Common Issues

#### Installation Fails
**Problem**: Permission denied or path not found
**Solution**:
```bash
# Check Claude Code installation
claude --version

# Verify Python version
python --version

# Check permissions
ls -la ~/.claude/
```

#### Configuration Not Loading
**Problem**: Claude Code not recognizing new configurations
**Solution**:
```bash
# Restart Claude Code session
# Or check configuration syntax:
python -m json.tool .claude/settings.json
```

#### Tools Not Found
**Problem**: Generated hooks fail because tools aren't installed
**Solution**:
```bash
# Install missing tools
npm install -g prettier eslint  # For frontend projects
pip install black ruff          # For Python projects
```

### Getting Help

1. **Check logs**: Installer creates detailed logs in `~/.claude/installer.log`
2. **Validate configs**: Use `claude config validate` to check syntax
3. **Reset configurations**: Use `claude config reset` to start fresh
4. **Community support**: Check GitHub issues or discussions

## Advanced Usage

### Team Collaboration

1. **Shared Configurations**: Commit `.claude/settings.json` to version control
2. **Personal Overrides**: Use `.claude/settings.local.json` for personal preferences
3. **Team Standards**: Use enterprise profile for organization-wide standards

### Continuous Integration

```yaml
# .github/workflows/claude-config.yml
name: Claude Config Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate Claude Config
        run: python claude-config-installer.py --validate
```

### Custom Profiles

Create your own profiles by extending the installer:

```python
# profiles/custom_profile.py
class CustomProfile(BaseProfile):
    def __init__(self):
        super().__init__("custom", "My Custom Profile")
    
    def detect(self, project_info):
        # Custom detection logic
        return project_info.has_file("custom.config")
    
    def generate_agents(self):
        # Custom agent generation
        pass
```

## Best Practices

1. **Start Simple**: Begin with recommended profile, customize later
2. **Version Control**: Always commit shared configurations
3. **Regular Updates**: Periodically re-run installer for updates
4. **Team Alignment**: Ensure team agrees on shared configurations
5. **Security**: Review generated permissions before production use

## Next Steps

After installation:
1. Test configurations with a small change
2. Customize agents and commands for your workflow
3. Train your team on new slash commands
4. Set up continuous validation in CI/CD
5. Contribute improvements back to the installer

---

For more information, visit the [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code) or check our [GitHub repository](https://github.com/your-org/claude-config-installer) for updates and community contributions.