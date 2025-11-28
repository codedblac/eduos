import os
import shutil
import subprocess

# --- SETTINGS ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
EXCLUDED_APPS = {'env', 'venv', '.venv', 'config', 'static', 'media', 'templates', 'node_modules', '.git', '__pycache__'}

def is_django_app(app_path):
    return os.path.isdir(app_path) and (
        os.path.isfile(os.path.join(app_path, 'models.py')) or os.path.isdir(os.path.join(app_path, 'migrations'))
    )

def delete_migrations(app_path):
    mig_dir = os.path.join(app_path, 'migrations')
    if os.path.isdir(mig_dir):
        for file in os.listdir(mig_dir):
            if file != '__init__.py' and file.endswith('.py'):
                os.remove(os.path.join(mig_dir, file))
        # Clean pycache too
        shutil.rmtree(os.path.join(mig_dir, '__pycache__'), ignore_errors=True)
        print(f"[✔] Cleared migrations in {app_path}")

def main():
    print("🧹 Resetting all migrations...")

    # Step 1: Delete all migration files
    for folder in os.listdir(PROJECT_ROOT):
        folder_path = os.path.join(PROJECT_ROOT, folder)
        if folder in EXCLUDED_APPS or not is_django_app(folder_path):
            continue
        delete_migrations(folder_path)

    # Step 2: Optional – Delete SQLite DB (edit this part if using PostgreSQL/MySQL)
    db_path = os.path.join(PROJECT_ROOT, 'db.sqlite3')
    if os.path.exists(db_path):
        os.remove(db_path)
        print("[🗑️] Deleted db.sqlite3")

    # Step 3: Recreate migrations
    print("[🔄] Making fresh migrations...")
    subprocess.run("python manage.py makemigrations", shell=True)

    # Step 4: Run migrations
    print("[🚀] Applying fresh migrations...")
    subprocess.run("python manage.py migrate", shell=True)

    print("[✅] Migration reset complete.")

if __name__ == "__main__":
    main()
