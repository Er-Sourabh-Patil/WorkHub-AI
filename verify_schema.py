#!/usr/bin/env python
import sqlite3

conn = sqlite3.connect('attendance.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check employees table columns
print("=== Employees Table Schema ===")
cursor.execute("PRAGMA table_info(employees)")
for row in cursor.fetchall():
    print(f"  {row[1]}: {row[2]}")

# Check announcements table exists
print("\n=== Announcements Table Schema ===")
try:
    cursor.execute("PRAGMA table_info(announcements)")
    for row in cursor.fetchall():
        print(f"  {row[1]}: {row[2]}")
except Exception as e:
    print(f"  Error: {e}")

# Check announcement_reads table exists
print("\n=== Announcement Reads Table Schema ===")
try:
    cursor.execute("PRAGMA table_info(announcement_reads)")
    for row in cursor.fetchall():
        print(f"  {row[1]}: {row[2]}")
except Exception as e:
    print(f"  Error: {e}")

conn.close()
print("\n✓ Database verification complete!")
