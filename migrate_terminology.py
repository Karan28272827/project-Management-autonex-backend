"""
Database migration script to rename tables for terminology refactoring.
Renames: parent_projects -> main_projects, projects -> sub_projects
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load .env file
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    exit(1)

# Create engine
engine = create_engine(DATABASE_URL)

print("Starting database migration...")

try:
    with engine.connect() as conn:
        # Step 1: Rename parent_projects to main_projects
        print("1. Renaming parent_projects -> main_projects...")
        conn.execute(text("ALTER TABLE parent_projects RENAME TO main_projects"))
        conn.commit()
        print("   ✓ Done")
        
        # Step 2: Rename projects to sub_projects
        print("2. Renaming projects -> sub_projects...")
        conn.execute(text("ALTER TABLE projects RENAME TO sub_projects"))
        conn.commit()
        print("   ✓ Done")
        
        # Step 3: Rename FK column
        print("3. Renaming parent_project_id -> main_project_id...")
        conn.execute(text("ALTER TABLE sub_projects RENAME COLUMN parent_project_id TO main_project_id"))
        conn.commit()
        print("   ✓ Done")
        
        # Step 4: Rename FK column in allocations table
        print("4. Updating allocations table FK column...")
        conn.execute(text("ALTER TABLE allocations RENAME COLUMN project_id TO sub_project_id"))
        conn.commit()
        print("   ✓ Done")
        
        print("\n✅ Migration completed successfully!")
        
except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    exit(1)
