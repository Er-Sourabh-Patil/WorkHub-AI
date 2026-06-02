#!/usr/bin/env python
import sqlite3

conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print("Tables in database:")
for table in tables:
    print(f"  ✓ {table[0]}")

# Check if announcements table exists
cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='announcements'")
if cursor.fetchone()[0] > 0:
    print("\n✓ Announcements table exists")
    cursor.execute("PRAGMA table_info(announcements)")
    cols = cursor.fetchall()
    print(f"  Columns: {len(cols)}")
    for col in cols:
        print(f"    - {col[1]} ({col[2]})")

# Check if announcement_reads table exists
cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='announcement_reads'")
if cursor.fetchone()[0] > 0:
    print("\n✓ Announcement reads table exists")

# Check employees table for new columns
cursor.execute("PRAGMA table_info(employees)")
cols = cursor.fetchall()
col_names = [col[1] for col in cols]
if 'email' in col_names:
    print("\n✓ Email column exists in employees table")
if 'contact_number' in col_names:
    print("✓ Contact number column exists in employees table")

conn.close()
