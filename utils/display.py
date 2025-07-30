"""
EIPAS Display Utilities
Handles user interface and messaging
"""
import sys

def display_banner():
    """Display installation banner"""
    banner = """🚀 EIPAS Enterprise Workflow Installer
==================================================
Installing Claude Code compliant EIPAS system...
- 5-phase enterprise workflow
- 32 specialized AI agents (29 working + 6 meta)
- Iterative implementation & QA cycles
- GitHub integration & automatic commits
- Resume capability & task hierarchy
"""
    print(banner)

def display_success():
    """Display success message"""
    success = """
🎉 EIPAS Installation Complete!
==================================================

Next steps:
1. Run: /eipas "your innovative idea"
2. Check status: /eipas status
3. Resume workflows: /eipas resume

Features installed:
✅ 5-phase enterprise workflow
✅ 32 specialized AI agents
  • 9 CXO evaluation agents (Phase 1)
  • 4 business analysis agents (Phase 2)
  • 5 product & architecture agents (Phase 3)
  • 4 implementation agents (Phase 4 - Iterative)
  • 4 QA specialist agents (Phase 5 - Iterative)
  • 6 workflow management agents (Meta)
✅ Iterative implementation & QA cycles
✅ Quality gates and analysis checkpoints
✅ Task hierarchy and progress tracking
✅ GitHub integration (when available)
✅ Resume capability for interrupted workflows

Configuration location: .claude/
Task database: .claude/tasks/memory.db
Backup (if existed): .claude-backup/
"""
    print(success)