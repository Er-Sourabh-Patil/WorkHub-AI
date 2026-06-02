#!/usr/bin/env python
import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print("Tables in database.db:")
for table in tables:
    print(f"  ✓ {table[0]}")

# Check if announcements table exists
print("\n=== Key Verification ===")
cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='announcements'")
if cursor.fetchone()[0] > 0:
    print("✓ Announcements table exists")

cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='announcement_reads'")
if cursor.fetchone()[0] > 0:
    print("✓ Announcement reads table exists")

# Check employees table for new columns
cursor.execute("PRAGMA table_info(employees)")
cols = cursor.fetchall()
col_names = [col[1] for col in cols]

print(f"\nEmployees table columns ({len(col_names)} total):")
for col in col_names:
    if col in ['email', 'contact_number']:
        print(f"  ✓ {col} (NEW)")
    else:
        print(f"  ✓ {col}")

conn.close()
print("\n✓ Database verification complete!")
