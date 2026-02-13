import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone, timedelta
import uuid
from dotenv import load_dotenv
from pathlib import Path
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

async def create_comprehensive_sample_data():
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🚀 Creating comprehensive sample data...\n")
    
    # Get admin user
    admin = await db.users.find_one({"email": "admin@e1invest.com"})
    if not admin:
        print("❌ Admin user not found. Run seed_data.py first!")
        return
    
    # Get existing properties
    properties = await db.properties.find({}, {"_id": 0}).to_list(length=10)
    if len(properties) == 0:
        print("❌ No properties found. Run seed_data.py first!")
        return
    
    print(f"✓ Found {len(properties)} properties")
    
    # 1. CREATE SAMPLE INVESTORS
    print("\n📊 Creating sample investors...")
    investors = []
    for i in range(5):
        investor = {
            "id": str(uuid.uuid4()),
            "email": f"investor{i+1}@example.com",
            "phone": f"+2348012345{i}00",
            "first_name": f"Investor",
            "last_name": f"User{i+1}",
            "role": "investor",
            "email_verified": True,
            "whatsapp_verified": True,
            "favorites": [properties[0]["id"], properties[1]["id"]],
            "referred_by": None if i == 0 else "REFADMIN123",
            "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(10, 100))).isoformat(),
            "updated_at": None
        }
        
        existing = await db.users.find_one({"email": investor["email"]})
        if not existing:
            await db.users.insert_one(investor)
            investors.append(investor)
    
    print(f"✓ Created {len(investors)} investors")
    
    # 2. CREATE INVESTMENTS
    print("\n💰 Creating sample investments...")
    investments_created = 0
    for i, investor in enumerate(investors):
        for j in range(random.randint(1, 3)):
            property_doc = random.choice(properties)
            investment = {
                "id": str(uuid.uuid4()),
                "user_id": investor["id"],
                "property_id": property_doc["id"],
                "amount": random.choice([2000000, 5000000, 8000000, 10000000]),
                "currency": "NGN",
                "instalment_plan": None,
                "status": random.choice(["active", "active", "active", "pending"]),
                "documents": [],
                "initial_transaction_id": None,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 90))).isoformat(),
                "updated_at": None
            }
            await db.investments.insert_one(investment)
            investments_created += 1
    
    print(f"✓ Created {investments_created} investments")
    
    # 3. CREATE MATERIALS & LABOUR PLANS
    print("\n🏗️ Creating materials & labour plans...")
    for i, property_doc in enumerate(properties[:3]):
        materials = [
            {"name": "Cement", "quantity_needed": 500, "unit": "bags", "estimated_cost": 5000},
            {"name": "Sand", "quantity_needed": 50, "unit": "tonnes", "estimated_cost": 15000},
            {"name": "Granite", "quantity_needed": 30, "unit": "tonnes", "estimated_cost": 20000},
            {"name": "Bricks", "quantity_needed": 10000, "unit": "pieces", "estimated_cost": 150},
            {"name": "Steel Rods", "quantity_needed": 200, "unit": "pieces", "estimated_cost": 8000},
        ]
        
        labour = [
            {"category": "Mason", "workers_needed": 5, "days_needed": 60, "cost_per_day": 10000},
            {"category": "Plumber", "workers_needed": 2, "days_needed": 30, "cost_per_day": 15000},
            {"category": "Electrician", "workers_needed": 2, "days_needed": 25, "cost_per_day": 15000},
            {"category": "Carpenter", "workers_needed": 3, "days_needed": 40, "cost_per_day": 12000},
        ]
        
        total_materials_cost = sum(m["quantity_needed"] * m["estimated_cost"] for m in materials)
        total_labour_cost = sum(l["workers_needed"] * l["days_needed"] * l["cost_per_day"] for l in labour)
        
        # Random progress
        materials_raised = total_materials_cost * random.uniform(0.3, 0.8)
        labour_raised = total_labour_cost * random.uniform(0.4, 0.9)
        
        plan = {
            "id": str(uuid.uuid4()),
            "property_id": property_doc["id"],
            "materials": materials,
            "labour": labour,
            "total_materials_cost": total_materials_cost,
            "total_labour_cost": total_labour_cost,
            "total_cost": total_materials_cost + total_labour_cost,
            "materials_raised": materials_raised,
            "labour_raised": labour_raised,
            "status": "fundraising",
            "created_by": admin["id"],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.materials_labour_plans.insert_one(plan)
    
    print("✓ Created 3 materials & labour plans with progress data")
    
    # 4. CREATE OCCUPANCY DATA
    print("\n🏠 Creating occupancy data...")
    for property_doc in properties:
        total_units = random.choice([10, 20, 30, 50])
        occupied = random.randint(int(total_units * 0.5), total_units)
        
        occupancy = {
            "id": str(uuid.uuid4()),
            "property_id": property_doc["id"],
            "total_units": total_units,
            "occupied_units": occupied,
            "available_units": total_units - occupied,
            "occupancy_rate": (occupied / total_units * 100),
            "notes": f"Last updated: {datetime.now().strftime('%Y-%m-%d')}",
            "updated_by": admin["id"],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.occupancy.update_one(
            {"property_id": property_doc["id"]},
            {"$set": occupancy},
            upsert=True
        )
    
    print(f"✓ Created occupancy data for {len(properties)} properties")
    
    # 5. CREATE EXIT REQUESTS
    print("\n🚪 Creating exit requests...")
    active_investments = await db.investments.find({"status": "active"}, {"_id": 0}).to_list(length=5)
    for investment in active_investments[:2]:
        exit_request = {
            "id": str(uuid.uuid4()),
            "investment_id": investment["id"],
            "user_id": investment["user_id"],
            "asking_price": investment["amount"] * random.uniform(1.05, 1.15),
            "original_investment": investment["amount"],
            "property_id": investment["property_id"],
            "reason": "Need liquidity for other investment",
            "status": random.choice(["pending", "approved"]),
            "urgent": random.choice([True, False]),
            "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))).isoformat(),
            "resolved_at": None
        }
        await db.exit_requests.insert_one(exit_request)
    
    print("✓ Created 2 exit requests (1 pending, 1 approved)")
    
    # 6. CREATE SUPPLIERS
    print("\n👷 Creating suppliers...")
    supplier_categories = ["construction", "plumbing", "electrical", "carpentry", "painting"]
    for i, category in enumerate(supplier_categories):
        supplier = {
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "business_name": f"{category.title()} Masters Ltd",
            "contact_person": f"Mr. {category.title()}",
            "phone": f"+234801234{i}678",
            "email": f"{category}@suppliers.com",
            "service_category": category,
            "years_experience": random.randint(5, 20),
            "portfolio_description": f"Professional {category} services with {random.randint(50, 200)}+ completed projects",
            "equity_interest": random.choice([True, False]),
            "status": random.choice(["approved", "approved", "pending"]),
            "rating": random.uniform(4.0, 5.0),
            "completed_projects": random.randint(10, 50),
            "total_equity_earned": random.uniform(0, 5),
            "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(30, 200))).isoformat()
        }
        await db.suppliers.insert_one(supplier)
    
    print(f"✓ Created {len(supplier_categories)} suppliers")
    
    # 7. CREATE APPOINTMENTS
    print("\n📅 Creating appointments...")
    for investor in investors[:3]:
        for j in range(random.randint(1, 2)):
            property_doc = random.choice(properties)
            appointment = {
                "id": str(uuid.uuid4()),
                "property_id": property_doc["id"],
                "user_id": investor["id"],
                "appointment_date": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                "appointment_time": random.choice(["10:00 AM", "2:00 PM", "4:00 PM"]),
                "visitor_name": f"{investor['first_name']} {investor['last_name']}",
                "visitor_phone": investor["phone"],
                "visitor_email": investor["email"],
                "notes": "Interested in investment opportunity",
                "status": random.choice(["pending", "confirmed", "pending"]),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.appointments.insert_one(appointment)
    
    print("✓ Created appointments for 3 investors")
    
    # 8. CREATE NOTIFICATIONS
    print("\n🔔 Creating notifications...")
    for investor in investors:
        for i in range(3):
            notification = {
                "id": str(uuid.uuid4()),
                "user_id": investor["id"],
                "title": random.choice([
                    "New Investment Opportunity",
                    "Appointment Confirmed",
                    "Investment Update",
                    "Exit Request Processed"
                ]),
                "message": random.choice([
                    "A new property matching your preferences is now available",
                    "Your viewing appointment has been confirmed",
                    "Your investment is performing well with 15% APY",
                    "Your exit request has been reviewed"
                ]),
                "read": random.choice([True, False, False]),
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 72))).isoformat()
            }
            await db.notifications.insert_one(notification)
    
    print(f"✓ Created notifications for {len(investors)} investors")
    
    # 9. CREATE SOCIAL POSTS
    print("\n📱 Creating social posts...")
    for i in range(10):
        user = random.choice([admin] + investors)
        property_doc = random.choice(properties) if random.choice([True, False]) else None
        
        post = {
            "id": str(uuid.uuid4()),
            "user_id": user["id"],
            "content": random.choice([
                "Just invested in this amazing property! Great returns guaranteed!",
                "Check out this investment opportunity in Oye Ekiti",
                "Happy with my investment returns so far. 15% APY is real!",
                "This property has excellent potential. Don't miss out!",
                "Secured my financial future with real estate investment"
            ]),
            "property_id": property_doc["id"] if property_doc else None,
            "investment_id": None,
            "images": [],
            "likes": [investors[j]["id"] for j in range(random.randint(1, 4))],
            "comments": [],
            "shares": random.randint(0, 10),
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 240))).isoformat()
        }
        await db.social_posts.insert_one(post)
    
    print("✓ Created 10 social posts")
    
    # 10. CREATE REFERRALS
    print("\n🎯 Creating referral data...")
    for investor in investors:
        referral = {
            "id": str(uuid.uuid4()),
            "code": f"REF{investor['id'][:8].upper()}",
            "user_id": investor["id"],
            "commission_rate": 5.0,
            "total_referrals": random.randint(0, 5),
            "total_commission_earned": random.uniform(0, 50000),
            "active": True,
            "created_at": investor["created_at"]
        }
        await db.referrals.insert_one(referral)
    
    print(f"✓ Created referral codes for {len(investors)} investors")
    
    client.close()
    
    print("\n" + "="*60)
    print("🎉 COMPREHENSIVE SAMPLE DATA CREATED SUCCESSFULLY!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"  • {len(investors)} Investors")
    print(f"  • {investments_created} Investments")
    print(f"  • 3 Materials & Labour Plans")
    print(f"  • {len(properties)} Properties with Occupancy Data")
    print(f"  • 2 Exit Requests")
    print(f"  • 5 Suppliers")
    print(f"  • Multiple Appointments")
    print(f"  • Notifications for all users")
    print(f"  • 10 Social Posts")
    print(f"  • Referral codes for all investors")
    print(f"\n✅ Platform ready for comprehensive testing!\n")

if __name__ == "__main__":
    asyncio.run(create_comprehensive_sample_data())
