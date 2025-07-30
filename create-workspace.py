#!/usr/bin/env python3
import os
import sys

def create_workspace(name):
    base = os.getenv('EIPAS_WORKSPACE')
    if not base:
        print("❌ EIPAS_WORKSPACE not set")
        print("Set it: export EIPAS_WORKSPACE=/path/to/workspace")
        sys.exit(1)
    
    path = os.path.join(os.path.expanduser(base), name)
    
    if os.path.exists(path):
        print(f"❌ Workspace '{name}' exists at {path}")
        sys.exit(1)
    
    try:
        dirs = [path] + [os.path.join(path, d) for d in ['phase1', 'phase2', 'phase3', 'phase4', 'phase5']]
        claude = os.path.join(path, '.claude')
        dirs += [claude] + [os.path.join(claude, d) for d in ['agents', 'hooks', 'commands']]
        
        for d in dirs:
            os.makedirs(d, exist_ok=True)
        
        with open(os.path.join(claude, 'settings.json'), 'w') as f:
            f.write('{}')
        
        print(f"✅ Created {name} at {path}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create-workspace.py <name>")
        sys.exit(1)
    
    create_workspace(sys.argv[1])