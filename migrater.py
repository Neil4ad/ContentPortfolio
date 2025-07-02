#!/usr/bin/env python3
"""
Standalone migration script to add show_business_goal_filter field
This script works directly with SQLite without importing your app
"""

import sqlite3
import os

def migrate_database():
    """Add the show_business_goal_filter column to the site_settings table"""
    
    # Find the database file
    db_paths = [
        'instance/portfolio.db',  # Instance folder
        'portfolio.db',           # Project root
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Could not find database file. Looked for:")
        for path in db_paths:
            print(f"   - {path}")
        return False
    
    print(f"📁 Found database at: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(site_settings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'show_business_goal_filter' in columns:
            print("✅ show_business_goal_filter column already exists")
            conn.close()
            return True
        
        # Add the new column with default value
        print("🔄 Adding show_business_goal_filter column...")
        cursor.execute('''
            ALTER TABLE site_settings 
            ADD COLUMN show_business_goal_filter BOOLEAN DEFAULT 1
        ''')
        
        # Commit the changes
        conn.commit()
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(site_settings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'show_business_goal_filter' in columns:
            print("✅ Successfully added show_business_goal_filter column")
            
            # Update any existing records to have the default value
            cursor.execute('''
                UPDATE site_settings 
                SET show_business_goal_filter = 1 
                WHERE show_business_goal_filter IS NULL
            ''')
            conn.commit()
            
            print("✅ Updated existing records with default value")
        else:
            print("❌ Failed to add column")
            return False
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Starting database migration...")
    success = migrate_database()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("You can now run your app with the new field.")
    else:
        print("\n💥 Migration failed!")
        print("You may need to manually add the field or check your database.")