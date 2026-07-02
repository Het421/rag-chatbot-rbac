import sys
import os

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

import pandas as pd
from backend.database import SessionLocal
from backend.auth.models import User
from backend.auth.utils import hash_password


def seed_users_from_csv(csv_path: str):
    print(f"Looking for CSV at: {os.path.abspath(csv_path)}")

    if not os.path.exists(csv_path):
        print("❌ CSV file not found!")
        return

    df = pd.read_csv(csv_path)
    print(f"Found {len(df)} rows in CSV")
    print(df)

    db = SessionLocal()
    inserted = 0
    skipped = 0

    for _, row in df.iterrows():
        existing = db.query(User).filter(
            User.employee_id == row["employee_id"]
        ).first()

        if existing:
            print(f"Skipping {row['employee_id']} — already exists.")
            skipped += 1
            continue

        if row["role"] not in ["admin", "employee"]:
            print(f"Skipping {row['employee_id']} — invalid role '{row['role']}'.")
            skipped += 1
            continue

        user = User(
            employee_id=row["employee_id"],
            full_name=row["full_name"],
            email=row["email"],
            hashed_password=hash_password(row["employee_id"]),
            role=row["role"],
            is_active=True
        )

        db.add(user)
        inserted += 1
        print(f"Added: {row['employee_id']} — {row['full_name']} ({row['role']})")

    db.commit()
    db.close()
    print(f"\n✅ Done! Inserted: {inserted}, Skipped: {skipped}")


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "scripts/users.csv"
    print(f"Script location: {__file__}")
    print(f"CSV path argument: {csv_path}")
    seed_users_from_csv(csv_path)