import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
import uuid
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

async def seed_database():
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Create admin user
    admin_user = {
        "id": str(uuid.uuid4()),
        "email": "admin@e1invest.com",
        "phone": None,
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin",
        "email_verified": True,
        "whatsapp_verified": False,
        "favorites": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": None
    }
    
    existing_admin = await db.users.find_one({"email": "admin@e1invest.com"})
    if not existing_admin:
        await db.users.insert_one(admin_user)
        print("✓ Admin user created: admin@e1invest.com")
    else:
        admin_user = existing_admin
        print("✓ Admin user already exists")
    
    # Sample properties
    properties = [
        {
            "id": str(uuid.uuid4()),
            "title": "Luxury 3-Bedroom Investment Apartment",
            "description": "Prime investment opportunity in the heart of Oye Ekiti. This modern 3-bedroom apartment offers exceptional rental yields with guaranteed returns. Perfect for both holiday stays and long-term rentals. Features include modern kitchen, spacious living area, and premium finishes throughout.",
            "property_type": "apartment",
            "location": "Oye Ekiti Central",
            "price": 8500000,
            "currency": "NGN",
            "images": [
                "https://images.unsplash.com/photo-1643297551340-19d8ad4f20ad?crop=entropy&cs=srgb&fm=jpg&q=85",
                "https://images.unsplash.com/photo-1757262798620-c2cc40cfb440?crop=entropy&cs=srgb&fm=jpg&q=85"
            ],
            "virtual_tour_url": None,
            "investment_details": {
                "rental_yield": 12.5,
                "apy": 15.0,
                "minimum_investment": 2000000,
                "maximum_investment": None,
                "exit_terms": "3-year lock-in with guaranteed buyback at 105% of original investment value. Early exit available after 2 years with 3% penalty.",
                "stay_eligibility": "14 complimentary nights per year for investors. Additional nights at 50% discount.",
                "guaranteed_returns": True
            },
            "features": [
                "Air Conditioning",
                "24/7 Security",
                "Backup Generator",
                "Swimming Pool Access",
                "Gym Facilities",
                "Parking Space",
                "High-Speed Internet",
                "Modern Kitchen"
            ],
            "availability": "available",
            "bedrooms": 3,
            "bathrooms": 2,
            "square_feet": 1200,
            "created_by": admin_user["id"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": None
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Student Hostel Investment Block",
            "description": "High-demand student accommodation near major institutions. This hostel block comprises 20 rooms with shared facilities, offering consistent occupancy rates year-round. Ideal for passive income seekers with minimal management requirements.",
            "property_type": "hostel",
            "location": "Oye Ekiti University Area",
            "price": 15000000,
            "currency": "NGN",
            "images": [
                "https://images.unsplash.com/photo-1585011191285-8b443579631c?crop=entropy&cs=srgb&fm=jpg&q=85"
            ],
            "virtual_tour_url": None,
            "investment_details": {
                "rental_yield": 18.0,
                "apy": 20.0,
                "minimum_investment": 5000000,
                "maximum_investment": None,
                "exit_terms": "5-year investment period with annual profit distribution. Exit possible after year 3 with board approval.",
                "stay_eligibility": "Not applicable - commercial investment only. Quarterly dividend payments.",
                "guaranteed_returns": True
            },
            "features": [
                "20 Furnished Rooms",
                "Shared Kitchen",
                "Common Study Area",
                "24/7 Security",
                "Water Supply",
                "Electricity",
                "Laundry Facilities",
                "Property Management Included"
            ],
            "availability": "available",
            "bedrooms": 20,
            "bathrooms": 10,
            "square_feet": 3500,
            "created_by": admin_user["id"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": None
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Premium Estate Block - Phase 1",
            "description": "Be part of Oye Ekiti's most prestigious residential estate development. This estate block offers exclusive investment opportunities with land appreciation potential and rental income. Early investors receive special pricing and priority allocation.",
            "property_type": "estate_block",
            "location": "Oye Ekiti New Development Zone",
            "price": 25000000,
            "currency": "NGN",
            "images": [
                "https://images.unsplash.com/photo-1685266326473-5b99c3d08a7e?crop=entropy&cs=srgb&fm=jpg&q=85",
                "https://images.unsplash.com/photo-1585011191285-8b443579631c?crop=entropy&cs=srgb&fm=jpg&q=85"
            ],
            "virtual_tour_url": None,
            "investment_details": {
                "rental_yield": 10.0,
                "apy": 18.0,
                "minimum_investment": 10000000,
                "maximum_investment": 50000000,
                "exit_terms": "7-year development period. Investors can exit after completion of Phase 1 (3 years) with profit sharing based on property appreciation.",
                "stay_eligibility": "Annual stays in estate properties once completed. Early investor privileges include lifetime discount.",
                "guaranteed_returns": False
            },
            "features": [
                "Gated Community",
                "Estate Clubhouse",
                "Sports Complex",
                "Shopping Center",
                "Schools & Healthcare",
                "24/7 Security",
                "Constant Power & Water",
                "Smart Home Ready",
                "Green Spaces & Parks"
            ],
            "availability": "available",
            "bedrooms": None,
            "bathrooms": None,
            "square_feet": 5000,
            "created_by": admin_user["id"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": None
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Compact Investment Unit",
            "description": "Perfect entry-level investment for first-time property investors. This 1-bedroom unit offers affordable access to the real estate market with strong rental demand from young professionals and students. Low maintenance, high returns.",
            "property_type": "investment_unit",
            "location": "Oye Ekiti Town Centre",
            "price": 3500000,
            "currency": "NGN",
            "images": [
                "https://images.unsplash.com/photo-1643297551340-19d8ad4f20ad?crop=entropy&cs=srgb&fm=jpg&q=85"
            ],
            "virtual_tour_url": None,
            "investment_details": {
                "rental_yield": 14.0,
                "apy": 16.5,
                "minimum_investment": 1000000,
                "maximum_investment": None,
                "exit_terms": "2-year minimum holding period. Flexible exit with 1-month notice after initial period.",
                "stay_eligibility": "7 complimentary nights per year. Perfect for occasional personal use.",
                "guaranteed_returns": True
            },
            "features": [
                "Furnished 1-Bedroom",
                "Modern Bathroom",
                "Kitchenette",
                "Air Conditioning",
                "Security",
                "Parking",
                "Internet Ready",
                "Low Maintenance"
            ],
            "availability": "available",
            "bedrooms": 1,
            "bathrooms": 1,
            "square_feet": 450,
            "created_by": admin_user["id"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": None
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Diaspora Special - 2BR Apartment",
            "description": "Designed specifically for diaspora investors seeking both investment returns and personal use during visits. This 2-bedroom apartment combines rental income potential with the flexibility of personal stays. Full property management included.",
            "property_type": "apartment",
            "location": "Oye Ekiti Airport Road",
            "price": 6000000,
            "currency": "NGN",
            "images": [
                "https://images.unsplash.com/photo-1757262798620-c2cc40cfb440?crop=entropy&cs=srgb&fm=jpg&q=85"
            ],
            "virtual_tour_url": None,
            "investment_details": {
                "rental_yield": 11.0,
                "apy": 14.0,
                "minimum_investment": 2000000,
                "maximum_investment": None,
                "exit_terms": "Flexible exit strategy. Sell anytime with company assistance at market rate. Priority buyback available.",
                "stay_eligibility": "Unlimited personal stays with 2-week advance notice. Property management handles rental scheduling.",
                "guaranteed_returns": True
            },
            "features": [
                "2 Bedrooms",
                "2 Bathrooms",
                "Full Kitchen",
                "Living & Dining Area",
                "Balcony",
                "Air Conditioning",
                "Parking",
                "Property Management",
                "Airport Proximity"
            ],
            "availability": "available",
            "bedrooms": 2,
            "bathrooms": 2,
            "square_feet": 850,
            "created_by": admin_user["id"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": None
        }
    ]
    
    # Insert properties
    existing_count = await db.properties.count_documents({})
    if existing_count == 0:
        await db.properties.insert_many(properties)
        print(f"✓ Created {len(properties)} sample properties")
    else:
        print(f"✓ Database already has {existing_count} properties")
    
    client.close()
    print("\n✓ Database seeding completed!")
    print(f"  - Admin email: admin@e1invest.com")
    print(f"  - Properties: {len(properties)}")
    print(f"  - You can now test the full application!\n")

if __name__ == "__main__":
    asyncio.run(seed_database())
