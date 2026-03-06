"""
Script to fix migration index creation by using IF NOT EXISTS
This is a workaround for the duplicate index error
"""
import re

migration_file = "alembic/versions/001_initial_schema.py"

with open(migration_file, 'r') as f:
    content = f.read()

# Replace op.create_index with op.execute using IF NOT EXISTS for custom indexes
# This is a workaround - the proper fix is to regenerate the migration

# Pattern to match: op.create_index('idx_...', 'table_name', [...], unique=False)
pattern = r"op\.create_index\('(idx_\w+)', '(\w+)', \[([^\]]+)\], unique=False\)"

def replace_index(match):
    index_name = match.group(1)
    table_name = match.group(2)
    columns = match.group(3)
    # Convert column list to SQL format
    cols = columns.replace("'", "").replace('"', '').split(',')
    cols_sql = ', '.join([c.strip() for c in cols])
    return f'''    # Create index if not exists
    op.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({cols_sql})")'''

new_content = re.sub(pattern, replace_index, content)

with open(migration_file, 'w') as f:
    f.write(new_content)

print(f"Fixed migration file: {migration_file}")
print("Note: This uses raw SQL with IF NOT EXISTS as a workaround")

