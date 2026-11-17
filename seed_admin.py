"""
Secure Admin Account Seeder
Creates an initial administrator account in the MySQL/SQLite database.
Usage:
    python seed_admin.py [--username admin] [--email admin@interviewportal.com] [--password YourSecurePassword]
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import Config
from database import init_db
from models.user import Admin
from dao.user_dao import AdminDAO

def seed_admin(username="admin", email="admin@interviewportal.com", password="AdminPassword123!"):
    # Ensure tables exist
    init_db()
    
    existing = AdminDAO.get_by_username(username) or AdminDAO.get_by_email(email)
    if existing:
        print(f"[INFO] Admin '{existing.username}' ({existing.email}) already exists. ID: {existing.id}")
        return existing.id

    password_hash = Admin.hash_password(password)
    admin_id = AdminDAO.create_admin(username, email, password_hash)
    print("=" * 60)
    print("ADMIN ACCOUNT CREATED SUCCESSFULLY!")
    print(f"Username : {username}")
    print(f"Email    : {email}")
    print(f"Password : {password}")
    print(f"Admin ID : {admin_id}")
    print("=" * 60)
    print("[SECURITY NOTICE] Please change this password upon first login.")
    return admin_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Admin Account")
    parser.add_argument("--username", default="admin", help="Admin username")
    parser.add_argument("--email", default="admin@interviewportal.com", help="Admin email")
    parser.add_argument("--password", default="AdminPassword123!", help="Admin password")
    
    args = parser.parse_args()
    seed_admin(args.username, args.email, args.password)
