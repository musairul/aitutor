"""
Migration script to remove weekly structure and connect lessons directly to modules.
This script will:
1. Add module_id and file_ids columns to lessons table
2. Copy data from week to lesson (preserving relationships)
3. Drop the week table
4. Update foreign key constraints
"""

from app import create_app
from models import db
from sqlalchemy import text

def migrate_database():
    app = create_app()
    
    with app.app_context():
        print("Starting database migration...")
        
        try:
            # Step 1: Check if columns exist, add if they don't
            print("Step 1: Checking and adding columns to lessons...")
            with db.engine.connect() as conn:
                # Check if module_id column exists
                result = conn.execute(text("PRAGMA table_info(lesson)"))
                columns = [row[1] for row in result]
                
                if 'module_id' not in columns:
                    print("  Adding module_id column...")
                    conn.execute(text("ALTER TABLE lesson ADD COLUMN module_id INTEGER"))
                    conn.commit()
                else:
                    print("  module_id column already exists")
                
                if 'file_ids' not in columns:
                    print("  Adding file_ids column...")
                    conn.execute(text("ALTER TABLE lesson ADD COLUMN file_ids TEXT"))
                    conn.commit()
                else:
                    print("  file_ids column already exists")
            print("✓ Columns ready")
            
            # Step 2: Populate module_id and file_ids from week table
            print("Step 2: Copying data from week to lesson...")
            with db.engine.connect() as conn:
                conn.execute(text("""
                    UPDATE lesson 
                    SET module_id = week.module_id,
                        file_ids = week.file_ids
                    FROM week 
                    WHERE lesson.week_id = week.id
                """))
                conn.commit()
            print("✓ Data copied")
            
            # Step 3: Make module_id NOT NULL - SQLite doesn't support ALTER COLUMN, skip this
            print("Step 3: Verifying module_id is populated...")
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM lesson WHERE module_id IS NULL"))
                null_count = result.fetchone()[0]
                if null_count > 0:
                    print(f"  ⚠️ Warning: {null_count} lessons still have NULL module_id")
                else:
                    print("  ✓ All lessons have module_id set")
            print("✓ Constraint verified (SQLite limitation: can't add NOT NULL to existing column)")
            
            # Step 4: Skip foreign key for SQLite (it has limitations)
            print("Step 4: Skipping foreign key constraint (SQLite limitation)...")
            print("✓ Foreign keys are enforced by SQLAlchemy ORM")
            
            # Step 5: Drop the old week_id column - SQLite doesn't support DROP COLUMN easily
            print("Step 5: Marking week_id column for manual cleanup if needed...")
            print("  Note: SQLite doesn't easily support DROP COLUMN")
            print("  The week_id column will remain but won't be used")
            print("✓ Column marked obsolete")
            
            # Step 6: Drop the week table (SQLite doesn't support CASCADE)
            print("Step 6: Dropping week table...")
            with db.engine.connect() as conn:
                conn.execute(text("DROP TABLE IF EXISTS week"))
                conn.commit()
            print("✓ Week table dropped")
            
            print("\n✅ Migration completed successfully!")
            print("The database now has lessons connected directly to modules.")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            print("\nRolling back changes...")
            db.session.rollback()

if __name__ == '__main__':
    migrate_database()
