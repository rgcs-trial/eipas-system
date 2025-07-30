#!/usr/bin/env python3
"""
Claude Code Configuration Installer

An intelligent installer that automatically detects project context and generates
optimized Claude Code configurations including agents, hooks, and commands.
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Version and metadata
__version__ = "1.0.0"
__author__ = "Claude Code Configuration Team"

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class ProjectInfo:
    """Container for project analysis results"""
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.config_files = {}
        self.package_managers = []
        self.frameworks = []
        self.languages = []
        self.tools = []
        self.ci_systems = []
        
    def has_file(self, filename: str) -> bool:
        """Check if project has a specific file"""
        return (self.root_path / filename).exists()
    
    def get_file_content(self, filename: str) -> Optional[str]:
        """Get content of a file if it exists"""
        file_path = self.root_path / filename
        if file_path.exists():
            try:
                return file_path.read_text(encoding='utf-8')
            except Exception:
                return None
        return None

class ClaudeConfigInstaller:
    """Main installer class for Claude Code configurations"""
    
    def __init__(self):
        self.setup_logging()
        self.project_info = None
        self.backup_path = None
        
    def setup_logging(self):
        """Configure logging for the installer"""
        log_dir = Path.home() / '.claude'
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'installer.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def print_banner(self):
        """Display the installer banner"""
        banner = f"""
{Colors.HEADER}╔═══════════════════════════════════════════════════════════════╗
║                 Claude Code Configuration Installer           ║
║                          Version {__version__}                         ║
╚═══════════════════════════════════════════════════════════════╝{Colors.ENDC}

{Colors.OKBLUE}Intelligent configuration generator for Claude Code{Colors.ENDC}
{Colors.OKCYAN}• Auto-detects your project's technology stack{Colors.ENDC}
{Colors.OKCYAN}• Generates optimized agents, hooks, and commands{Colors.ENDC}
{Colors.OKCYAN}• Supports team collaboration and enterprise policies{Colors.ENDC}
"""
        print(banner)
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        self.logger.info("Checking prerequisites...")
        
        # Check Claude Code installation
        try:
            result = subprocess.run(['claude', '--version'], 
                                 capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                print(f"{Colors.FAIL}✗ Claude Code not found or not accessible{Colors.ENDC}")
                print("  Please install Claude Code and ensure it's in your PATH")
                return False
            print(f"{Colors.OKGREEN}✓ Claude Code found{Colors.ENDC}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"{Colors.FAIL}✗ Claude Code not found or not accessible{Colors.ENDC}")
            print("  Please install Claude Code and ensure it's in your PATH")
            return False
        
        # Check Python version
        if sys.version_info < (3, 8):
            print(f"{Colors.FAIL}✗ Python 3.8+ required, found {sys.version_info.major}.{sys.version_info.minor}{Colors.ENDC}")
            return False
        print(f"{Colors.OKGREEN}✓ Python {sys.version_info.major}.{sys.version_info.minor} detected{Colors.ENDC}")
        
        return True
    
    def get_installation_scope(self) -> Tuple[str, Path]:
        """Get user choice for installation scope and return type and path"""
        print(f"\n{Colors.BOLD}Choose Installation Scope:{Colors.ENDC}")
        print("1. Project Level - Configurations shared with your team (.claude/ in project)")
        print("2. User Level - Personal configurations across all projects (~/.claude/)")
        
        while True:
            choice = input(f"\n{Colors.OKCYAN}Enter your choice (1/2): {Colors.ENDC}").strip()
            
            if choice == '1':
                # Project level installation
                project_path = Path.cwd()
                if not self._is_valid_project_directory(project_path):
                    print(f"{Colors.WARNING}Warning: No version control detected in current directory{Colors.ENDC}")
                    confirm = input("Continue anyway? (y/N): ").strip().lower()
                    if confirm != 'y':
                        continue
                
                claude_path = project_path / '.claude'
                return 'project', claude_path
            
            elif choice == '2':
                # User level installation
                claude_path = Path.home() / '.claude'
                return 'user', claude_path
            
            else:
                print(f"{Colors.FAIL}Invalid choice. Please enter 1 or 2.{Colors.ENDC}")
    
    def _is_valid_project_directory(self, path: Path) -> bool:
        """Check if directory appears to be a valid project"""
        vcs_indicators = ['.git', '.hg', '.svn']
        project_indicators = ['package.json', 'pyproject.toml', 'Cargo.toml', 'pom.xml', 'build.gradle']
        
        # Check for version control
        for indicator in vcs_indicators:
            if (path / indicator).exists():
                return True
        
        # Check for project files
        for indicator in project_indicators:
            if (path / indicator).exists():
                return True
        
        return False
    
    def analyze_project(self, project_path: Path) -> ProjectInfo:
        """Analyze project to determine technology stack and tools"""
        print(f"\n{Colors.BOLD}Analyzing Project...{Colors.ENDC}")
        self.logger.info(f"Analyzing project at: {project_path}")
        
        info = ProjectInfo(project_path)
        
        # Detect configuration files
        config_files = {
            'package.json': 'npm/yarn project',
            'pyproject.toml': 'Python project with modern packaging',
            'requirements.txt': 'Python project with pip',
            'Cargo.toml': 'Rust project',
            'pom.xml': 'Maven Java project',
            'build.gradle': 'Gradle project',
            'composer.json': 'PHP project',
            'go.mod': 'Go project'
        }
        
        for filename, description in config_files.items():
            if info.has_file(filename):
                info.config_files[filename] = description
                print(f"{Colors.OKGREEN}  ✓ {filename}{Colors.ENDC} - {description}")
        
        # Analyze package.json for JavaScript/TypeScript projects
        self._analyze_package_json(info)
        
        # Analyze Python projects
        self._analyze_python_project(info)
        
        # Detect development tools
        self._detect_development_tools(info)
        
        # Detect CI/CD systems
        self._detect_ci_systems(info)
        
        self.project_info = info
        return info
    
    def _analyze_package_json(self, info: ProjectInfo):
        """Analyze package.json for Node.js project details"""
        package_json_content = info.get_file_content('package.json')
        if not package_json_content:
            return
        
        try:
            package_data = json.loads(package_json_content)
            dependencies = {**package_data.get('dependencies', {}), 
                          **package_data.get('devDependencies', {})}
            
            # Detect frameworks
            frameworks = {
                'react': 'React',
                'vue': 'Vue.js',
                '@angular/core': 'Angular',
                'next': 'Next.js',
                'nuxt': 'Nuxt.js',
                'express': 'Express.js',
                'fastify': 'Fastify',
                'koa': 'Koa.js'
            }
            
            for dep, framework in frameworks.items():
                if dep in dependencies:
                    info.frameworks.append(framework)
            
            # Detect tools
            tools = {
                'typescript': 'TypeScript',
                'eslint': 'ESLint',
                'prettier': 'Prettier',
                'jest': 'Jest',
                'vitest': 'Vitest',
                'webpack': 'Webpack',
                'vite': 'Vite',
                'rollup': 'Rollup'
            }
            
            for dep, tool in tools.items():
                if dep in dependencies:
                    info.tools.append(tool)
            
            info.languages.append('JavaScript')
            if 'typescript' in dependencies:
                info.languages.append('TypeScript')
                
        except json.JSONDecodeError:
            self.logger.warning("Could not parse package.json")
    
    def _analyze_python_project(self, info: ProjectInfo):
        """Analyze Python project structure and dependencies"""
        python_files = [f for f in info.root_path.rglob('*.py') if not f.name.startswith('.')]
        if not python_files and not any(info.has_file(f) for f in ['pyproject.toml', 'requirements.txt', 'setup.py']):
            return
        
        info.languages.append('Python')
        
        # Check for common Python frameworks
        requirements_content = info.get_file_content('requirements.txt')
        pyproject_content = info.get_file_content('pyproject.toml')
        
        frameworks = {
            'django': 'Django',
            'fastapi': 'FastAPI',
            'flask': 'Flask',
            'streamlit': 'Streamlit',
            'pandas': 'Data Science (Pandas)',
            'numpy': 'Data Science (NumPy)',
            'scikit-learn': 'Machine Learning',
            'tensorflow': 'TensorFlow',
            'pytorch': 'PyTorch'
        }
        
        content_to_check = (requirements_content or '') + (pyproject_content or '')
        for dep, framework in frameworks.items():
            if dep in content_to_check.lower():
                info.frameworks.append(framework)
        
        # Check for Python tools
        tools = ['black', 'ruff', 'mypy', 'pytest', 'flake8', 'isort']
        for tool in tools:
            if tool in content_to_check.lower():
                info.tools.append(tool.title())
    
    def _detect_development_tools(self, info: ProjectInfo):
        """Detect development tools and configurations"""
        tool_files = {
            '.eslintrc.js': 'ESLint',
            '.eslintrc.json': 'ESLint',
            '.prettierrc': 'Prettier',
            'jest.config.js': 'Jest',
            'vitest.config.js': 'Vitest',
            'webpack.config.js': 'Webpack',
            'vite.config.js': 'Vite',
            'rollup.config.js': 'Rollup',
            'tsconfig.json': 'TypeScript',
            'pyproject.toml': 'Python Tools',
            'setup.cfg': 'Python Tools',
            'tox.ini': 'Tox',
            'Dockerfile': 'Docker',
            'docker-compose.yml': 'Docker Compose'
        }
        
        for filename, tool in tool_files.items():
            if info.has_file(filename):
                if tool not in info.tools:
                    info.tools.append(tool)
    
    def _detect_ci_systems(self, info: ProjectInfo):
        """Detect CI/CD systems"""
        ci_indicators = {
            '.github/workflows': 'GitHub Actions',
            '.gitlab-ci.yml': 'GitLab CI',
            'azure-pipelines.yml': 'Azure Pipelines',
            '.travis.yml': 'Travis CI',
            'circle.yml': 'CircleCI',
            '.circleci/config.yml': 'CircleCI',
            'jenkinsfile': 'Jenkins'
        }
        
        for path, system in ci_indicators.items():
            if (info.root_path / path).exists():
                info.ci_systems.append(system)
    
    def recommend_profile(self, info: ProjectInfo) -> str:
        """Recommend installation profile based on project analysis"""
        print(f"\n{Colors.BOLD}Recommended Configuration Profile:{Colors.ENDC}")
        
        # Frontend detection
        frontend_indicators = ['React', 'Vue.js', 'Angular', 'Next.js', 'Nuxt.js']
        if any(fw in info.frameworks for fw in frontend_indicators):
            print(f"{Colors.OKGREEN}  → web-frontend{Colors.ENDC} - Optimized for frontend development")
            return 'web-frontend'
        
        # Backend API detection
        backend_indicators = ['Express.js', 'Django', 'FastAPI', 'Flask', 'Fastify', 'Koa.js']
        if any(fw in info.frameworks for fw in backend_indicators):
            print(f"{Colors.OKGREEN}  → backend-api{Colors.ENDC} - Optimized for API development")
            return 'backend-api'
        
        # Data Science detection
        data_indicators = ['Data Science (Pandas)', 'Data Science (NumPy)', 'Machine Learning', 'TensorFlow', 'PyTorch', 'Streamlit']
        if any(fw in info.frameworks for fw in data_indicators):
            print(f"{Colors.OKGREEN}  → data-science{Colors.ENDC} - Optimized for data science workflows")
            return 'data-science'
        
        # DevOps detection
        devops_indicators = ['Docker', 'Docker Compose']
        if any(tool in info.tools for tool in devops_indicators) or info.has_file('terraform'):
            print(f"{Colors.OKGREEN}  → devops{Colors.ENDC} - Optimized for infrastructure and deployment")
            return 'devops'
        
        # Default to general development
        print(f"{Colors.OKGREEN}  → general{Colors.ENDC} - General development configuration")
        return 'general'
    
    def run_installation(self, scope: str, claude_path: Path, profile: str, dry_run: bool = False):
        """Execute the installation process"""
        print(f"\n{Colors.BOLD}Installing Configuration...{Colors.ENDC}")
        
        if not dry_run:
            # Create backup if configurations exist
            self._backup_existing_configs(claude_path)
            
            # Create directory structure
            self._create_directory_structure(claude_path)
            
            # Generate and install configurations
            self._install_profile_configs(claude_path, profile)
            
            print(f"\n{Colors.OKGREEN}✓ Installation completed successfully!{Colors.ENDC}")
            print(f"  Configuration path: {claude_path}")
            
            if scope == 'project':
                print(f"\n{Colors.WARNING}Note: Add .claude/settings.local.json to .gitignore for personal settings{Colors.ENDC}")
        else:
            print(f"\n{Colors.OKCYAN}DRY RUN - No changes made{Colors.ENDC}")
            print(f"  Would install {profile} profile to: {claude_path}")
    
    def _backup_existing_configs(self, claude_path: Path):
        """Backup existing Claude configurations"""
        if not claude_path.exists():
            return
        
        timestamp = str(int(os.path.getmtime(claude_path)))
        backup_path = claude_path.parent / f"claude-backup-{timestamp}"
        
        print(f"  Backing up existing configurations to: {backup_path}")
        shutil.copytree(claude_path, backup_path)
        self.backup_path = backup_path
        self.logger.info(f"Created backup at: {backup_path}")
    
    def _create_directory_structure(self, claude_path: Path):
        """Create the Claude configuration directory structure"""
        directories = ['agents', 'commands', 'hooks']
        
        claude_path.mkdir(parents=True, exist_ok=True)
        for directory in directories:
            (claude_path / directory).mkdir(exist_ok=True)
        
        self.logger.info(f"Created directory structure at: {claude_path}")
    
    def _install_profile_configs(self, claude_path: Path, profile: str):
        """Install configuration files for the selected profile"""
        # This is a placeholder - in a full implementation, this would:
        # 1. Load profile-specific templates
        # 2. Generate context-aware configurations
        # 3. Write files to the claude_path
        
        # Create basic settings.json
        settings = {
            "profile": profile,
            "version": __version__,
            "generated_by": "claude-config-installer",
            "hooks": {},
            "tools": {
                "permissions": {
                    "Bash": ["allow"],
                    "Edit": ["allow"],
                    "Read": ["allow"],
                    "Write": ["allow"]
                }
            }
        }
        
        settings_path = claude_path / 'settings.json'
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
        
        print(f"  Generated settings.json")
        self.logger.info(f"Generated configuration for profile: {profile}")

def main():
    """Main entry point for the installer"""
    parser = argparse.ArgumentParser(description='Claude Code Configuration Installer')
    parser.add_argument('--profile', choices=['web-frontend', 'backend-api', 'data-science', 'devops', 'enterprise', 'custom'], 
                       help='Force specific installation profile')
    parser.add_argument('--path', type=Path, help='Custom installation path')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without installing')
    parser.add_argument('--backup', action='store_true', help='Only backup existing configurations')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    
    args = parser.parse_args()
    
    installer = ClaudeConfigInstaller()
    installer.print_banner()
    
    # Check prerequisites
    if not installer.check_prerequisites():
        sys.exit(1)
    
    # Handle backup-only mode
    if args.backup:
        claude_path = Path.home() / '.claude'
        if claude_path.exists():
            installer._backup_existing_configs(claude_path)
            print(f"{Colors.OKGREEN}✓ Backup completed{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}No existing configurations found to backup{Colors.ENDC}")
        return
    
    # Get installation scope and path
    if args.path:
        scope = 'custom'
        claude_path = args.path / '.claude'
    else:
        scope, claude_path = installer.get_installation_scope()
    
    # Analyze project if we're in a project directory
    project_path = Path.cwd()
    project_info = installer.analyze_project(project_path)
    
    # Recommend or use specified profile
    if args.profile:
        profile = args.profile
        print(f"\n{Colors.BOLD}Using specified profile: {profile}{Colors.ENDC}")
    else:
        profile = installer.recommend_profile(project_info)
        
        # Confirm profile choice
        confirm = input(f"\n{Colors.OKCYAN}Use recommended profile '{profile}'? (Y/n): {Colors.ENDC}").strip().lower()
        if confirm == 'n':
            print("Available profiles: web-frontend, backend-api, data-science, devops, enterprise")
            profile = input("Enter preferred profile: ").strip()
    
    # Run installation
    installer.run_installation(scope, claude_path, profile, args.dry_run)

if __name__ == '__main__':
    main()