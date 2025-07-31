"""
EIPAS Database Installation
Installs comprehensive SQLite database schema from template files
"""
import sqlite3
from pathlib import Path

class DatabaseInstaller:
    """Installs EIPAS database schema from template library"""
    
    def __init__(self, eipas_dir):
        self.eipas_dir = Path(eipas_dir)
        self.database_dir = self.eipas_dir / "database"
        self.db_path = self.database_dir / "memory.db"
        self.installer_dir = Path(__file__).parent.parent
        self.templates_dir = self.installer_dir / "database-templates"
    
    def install(self):
        """Install comprehensive SQLite database from template schema"""
        self.database_dir.mkdir(exist_ok=True)
        
        schema_template = self.templates_dir / "schema.sql"
        
        if not schema_template.exists():
            print(f"    ⚠️  Database schema template not found: {schema_template}")
            print(f"    📁 Create schema.sql in database-templates/ directory")
            return
        
        # Read schema from template
        with open(schema_template, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema_sql)
            conn.commit()
        
        print("  ✅ Initialized comprehensive SQLite database with EIPAS schema from template")