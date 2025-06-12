import asyncio
import random
from datetime import datetime, timedelta

# This is a standalone script, so we need to adjust the path to import from the app
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models import UnsubscribedEmail

async def main():
    print("Connecting to the database...")
    db = SessionLocal()
    
    print("Deleting existing data...")
    db.query(UnsubscribedEmail).delete()
    db.commit()

    print("Generating 55 new sample records...")
    records = []
    for i in range(55):
        records.append(
            UnsubscribedEmail(
                sender_name=f"Spammer #{i+1}",
                sender_email=f"spammer{i+1}@spam.com",
                unsub_method=random.choice(["direct_link", "isp_level"]),
                inserted_at=datetime.now() - timedelta(hours=i*2)
            )
        )

    db.add_all(records)
    db.commit()
    db.close()
    print("Done. 55 records created.")

if __name__ == "__main__":
    asyncio.run(main())