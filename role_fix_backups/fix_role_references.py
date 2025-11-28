# fix_role_references.py
import os
import re
import shutil

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(PROJECT_ROOT, "role_fix_backups")

# Patterns to check/fix
PATTERNS = {
    r"\brole\s*=": "primary_role=",
    r"\.primary_role\b": ".primary_role",
    r"['\"]role['\"]": "'primary_role'",
    r"CustomUser\.Role\.TEACHER": "'TEACHER'",
    r"CustomUser\.Role\.STUDENT": "'STUDENT'",
    r"CustomUser\.Role\.STAFF": "'STAFF'",
}

# Filters that are not model fields
VIRTUAL_FILTERS = ["name", "date_joined_after", "date_joined_before"]

def safe_backup(path):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backup_path = os.path.join(BACKUP_DIR, os.path.relpath(path, PROJECT_ROOT).replace(os.sep, "__"))
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    shutil.copy2(path, backup_path)

def fix_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    modified = content
    # Replace all patterns
    for pattern, replacement in PATTERNS.items():
        modified = re.sub(pattern, replacement, modified)

    # Fix Meta.fields containing old role or virtual fields
    def fix_meta_fields(match):
        fields_line = match.group(1)
        for f in VIRTUAL_FILTERS + ['primary_role']:
            fields_line = re.sub(rf"['\"]{f}['\"]", '', fields_line)
        # Remove extra commas and whitespace
        fields_line = re.sub(r",\s*,", ",", fields_line)
        fields_line = re.sub(r"\[\s*,", "[", fields_line)
        fields_line = re.sub(r",\s*\]", "]", fields_line)
        return f"fields = {fields_line}"

    modified = re.sub(r"fields\s*=\s*(\[[^\]]*\])", fix_meta_fields, modified)

    if modified != content:
        safe_backup(path)
        with open(path, "w", encoding="utf-8") as f:
            f.write(modified)
        print(f"[FIXED] {path}")

def walk_and_fix():
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Skip virtualenvs and migrations
        if any(x in root for x in ("venv", ".venv", "migrations")):
            continue
        for filename in files:
            if filename.endswith(".py"):
                fix_file(os.path.join(root, filename))

if __name__ == "__main__":
    print("🔍 Scanning project for old 'primary_role' references and Meta.fields issues...")
    walk_and_fix()
    print("\n✅ Scan & fixes complete! Backups in:", BACKUP_DIR)
