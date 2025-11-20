"""
Script to migrate the existing database by adding new columns.
This will PRESERVE your existing data.
"""
import sqlite3
import os

def migrate_database():
    # Check both possible locations
    db_paths = ['ai_tutor.db', 'instance/ai_tutor.db']
    db_path = None
    
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print(f"❌ Database not found in any of these locations: {db_paths}")
        print("   Run recreate_db.py instead to create a new database.")
        return
    
    print(f"🔧 Migrating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(module)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add processing_step column if it doesn't exist
        if 'processing_step' not in columns:
            print("   Adding processing_step column...")
            cursor.execute("ALTER TABLE module ADD COLUMN processing_step VARCHAR(200)")
            print("   ✓ processing_step column added")
        else:
            print("   ⚠️  processing_step column already exists")
        
        # Add processing_progress column if it doesn't exist
        if 'processing_progress' not in columns:
            print("   Adding processing_progress column...")
            cursor.execute("ALTER TABLE module ADD COLUMN processing_progress INTEGER DEFAULT 0")
            print("   ✓ processing_progress column added")
        else:
            print("   ⚠️  processing_progress column already exists")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        print("   Your existing data has been preserved.")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
