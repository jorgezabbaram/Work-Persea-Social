import asyncio
from uuid import UUID

from infrastructure.database import get_db_session
from infrastructure.repository import InventoryRepository
from domain.models import InventoryItem

async def seed_data():
    async for session in get_db_session():
        repo = InventoryRepository(session)
        
        try:
            # Product 1
            product1 = InventoryItem(
                product_id=UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
                quantity_available=100
            )
            await repo.create(product1)
            
            # Product 2
            product2 = InventoryItem(
                product_id=UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),
                quantity_available=50
            )
            await repo.create(product2)
            
            print("Data seeded successfully!")
        except Exception as e:
            if "UniqueViolation" in str(e) or "already exists" in str(e):
                 print("Data already seeded. Skipping.")
            else:
                 print(f"Seeding failed (ignorable if duplication): {e}")

if __name__ == "__main__":
    asyncio.run(seed_data())
