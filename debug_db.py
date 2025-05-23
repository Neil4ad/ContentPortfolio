# Database Sync Debugging Script
# Run this to diagnose the database synchronization issue

import os
import sqlite3
from datetime import datetime

def debug_database_sync():
    """
    Comprehensive debugging script to identify database sync issues
    """
    print("🔍 DATABASE SYNC DEBUGGING REPORT")
    print("=" * 50)
    print(f"Debug run at: {datetime.now()}")
    print()
    
    # 1. Check for multiple database files
    print("1. CHECKING FOR MULTIPLE DATABASE FILES")
    print("-" * 40)
    
    db_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.db') or file.endswith('.sqlite') or file.endswith('.sqlite3'):
                full_path = os.path.join(root, file)
                size = os.path.getsize(full_path)
                modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                db_files.append((full_path, size, modified))
                print(f"Found DB: {full_path}")
                print(f"  Size: {size} bytes")
                print(f"  Modified: {modified}")
                print()
    
    if len(db_files) > 1:
        print("⚠️  WARNING: Multiple database files found!")
        print("This could be causing the sync issue.")
        print()
    
    # 2. Check database connections in code
    print("2. CHECKING DATABASE CONFIGURATION")
    print("-" * 40)
    
    # Look for common Flask app files
    app_files = ['app.py', 'main.py', 'run.py', '__init__.py']
    config_files = ['config.py', 'settings.py']
    
    for filename in app_files + config_files:
        if os.path.exists(filename):
            print(f"Found config file: {filename}")
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for database configuration
                if 'DATABASE' in content.upper() or 'SQLALCHEMY' in content.upper():
                    print(f"  Contains database config")
                    
                    # Extract database-related lines
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        line_upper = line.upper()
                        if any(keyword in line_upper for keyword in ['DATABASE', 'SQLALCHEMY', 'DB_', 'SQLITE']):
                            print(f"  Line {i+1}: {line.strip()}")
            except Exception as e:
                print(f"  Error reading {filename}: {e}")
            print()
    
    # 3. Compare database contents
    print("3. COMPARING DATABASE CONTENTS")
    print("-" * 40)
    
    for db_path, size, modified in db_files:
        print(f"Analyzing database: {db_path}")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"  Tables: {[table[0] for table in tables]}")
            
            # Check for projects table
            if any('project' in table[0].lower() for table in tables):
                project_table = None
                for table in tables:
                    if 'project' in table[0].lower():
                        project_table = table[0]
                        break
                
                if project_table:
                    print(f"  Found projects table: {project_table}")
                    
                    # Get table schema
                    cursor.execute(f"PRAGMA table_info({project_table});")
                    columns = cursor.fetchall()
                    print(f"  Columns: {[col[1] for col in columns]}")
                    
                    # Count records
                    cursor.execute(f"SELECT COUNT(*) FROM {project_table};")
                    count = cursor.fetchone()[0]
                    print(f"  Record count: {count}")
                    
                    # Show recent changes (if there's a timestamp column)
                    timestamp_cols = ['updated_at', 'modified', 'last_modified', 'created_at']
                    timestamp_col = None
                    
                    for col in columns:
                        if col[1].lower() in timestamp_cols:
                            timestamp_col = col[1]
                            break
                    
                    if timestamp_col:
                        cursor.execute(f"SELECT id, title, {timestamp_col} FROM {project_table} ORDER BY {timestamp_col} DESC LIMIT 5;")
                        recent = cursor.fetchall()
                        print(f"  Recent records (by {timestamp_col}):")
                        for record in recent:
                            print(f"    ID: {record[0]}, Title: {record[1]}, {timestamp_col}: {record[2]}")
                    else:
                        # Just show first few records
                        cursor.execute(f"SELECT * FROM {project_table} LIMIT 3;")
                        records = cursor.fetchall()
                        print(f"  Sample records:")
                        for record in records:
                            print(f"    {record}")
            
            conn.close()
            
        except Exception as e:
            print(f"  Error analyzing database: {e}")
        
        print()
    
    # 4. Check for Flask app factory pattern or multiple app instances
    print("4. CHECKING FLASK APPLICATION PATTERN")
    print("-" * 40)
    
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip common non-relevant directories
        if any(skip_dir in root for skip_dir in ['.git', '__pycache__', 'node_modules', '.env']):
            continue
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    app_instances = 0
    database_configs = 0
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if 'Flask(__name__)' in content:
                    app_instances += 1
                    print(f"Flask app instance found in: {py_file}")
                
                if 'SQLALCHEMY_DATABASE_URI' in content:
                    database_configs += 1
                    print(f"Database config found in: {py_file}")
                    
        except Exception as e:
            continue
    
    print(f"Total Flask app instances: {app_instances}")
    print(f"Total database configs: {database_configs}")
    
    if app_instances > 1:
        print("⚠️  WARNING: Multiple Flask app instances found!")
        print("This could cause different parts of your app to use different databases.")
    
    print()
    
    # 5. Generate recommendations
    print("5. RECOMMENDATIONS")
    print("-" * 40)
    
    if len(db_files) > 1:
        print("🔧 Multiple database files detected:")
        print("   - Ensure all routes use the same database file")
        print("   - Check if admin and main app have different database configs")
        print("   - Consider consolidating to a single database file")
        print()
    
    if app_instances > 1:
        print("🔧 Multiple Flask app instances detected:")
        print("   - Ensure all routes are registered with the same app instance")
        print("   - Check for app factory pattern inconsistencies")
        print("   - Verify database initialization happens once")
        print()
    
    print("🔧 General troubleshooting steps:")
    print("   1. Add database commit logging to admin routes")
    print("   2. Add database query logging to display routes")
    print("   3. Check Flask-SQLAlchemy session handling")
    print("   4. Verify template variables are pulling from correct source")
    print("   5. Test database changes directly with SQLite browser")
    
    print()
    print("🚀 NEXT STEPS:")
    print("   1. Share your main Flask app file (app.py)")
    print("   2. Share admin route handlers")
    print("   3. Share project display templates")
    print("   4. Run this script and share results")

if __name__ == "__main__":
    debug_database_sync()