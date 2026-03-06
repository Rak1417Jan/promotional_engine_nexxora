#!/usr/bin/env python3
"""
Seed Sample Data Script
Creates sample operators, players, events, campaigns, and segments
"""
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import Operator, Player, Event, Segment, Campaign
from app.utils.logger import logger

def seed_sample_data():
    """Create sample data for testing"""
    db = SessionLocal()
    
    try:
        print("🌱 Seeding sample data...")
        
        # 1. Create Operators
        print("Creating operators...")
        operator1 = Operator(
            name="Lucky Casino",
            domain_url="luckycasino.example.com",
            contact_email="admin@luckycasino.com",
            commission_rate=Decimal("0.05"),
            pg_fee_rate=Decimal("0.02"),
            provider_fee_rate=Decimal("0.03")
        )
        db.add(operator1)
        
        operator2 = Operator(
            name="BetZone",
            domain_url="betzone.example.com",
            contact_email="admin@betzone.com",
            commission_rate=Decimal("0.06"),
            pg_fee_rate=Decimal("0.025"),
            provider_fee_rate=Decimal("0.035")
        )
        db.add(operator2)
        db.commit()
        db.refresh(operator1)
        db.refresh(operator2)
        print(f"✅ Created operators: {operator1.name}, {operator2.name}")
        
        # 2. Create Segments
        print("Creating segments...")
        high_value_segment = Segment(
            operator_id=operator1.id,
            name="High Value Players",
            description="Players with high lifetime value",
            segment_type="rfm",
            criteria={"status": "active", "ltv_min": 1000},
            player_count=0
        )
        db.add(high_value_segment)
        
        new_players_segment = Segment(
            operator_id=operator1.id,
            name="New Players",
            description="Recently registered players",
            segment_type="behavioral",
            criteria={"status": "new", "days_since_registration_max": 7},
            player_count=0
        )
        db.add(new_players_segment)
        db.commit()
        db.refresh(high_value_segment)
        db.refresh(new_players_segment)
        print(f"✅ Created segments: {high_value_segment.name}, {new_players_segment.name}")
        
        # 3. Create Players
        print("Creating players...")
        players_data = [
            {
                "operator_id": operator1.id,
                "external_player_id": "PLAYER001",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "status": "active",
                "total_deposits": Decimal("5000.00"),
                "total_bets": Decimal("8000.00"),
                "lifetime_value": Decimal("1200.00"),
                "segment_id": high_value_segment.id
            },
            {
                "operator_id": operator1.id,
                "external_player_id": "PLAYER002",
                "email": "jane.smith@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "phone": "+1234567891",
                "status": "new",
                "total_deposits": Decimal("100.00"),
                "total_bets": Decimal("50.00"),
                "lifetime_value": Decimal("50.00"),
                "segment_id": new_players_segment.id
            },
            {
                "operator_id": operator1.id,
                "external_player_id": "PLAYER003",
                "email": "bob.wilson@example.com",
                "first_name": "Bob",
                "last_name": "Wilson",
                "phone": "+1234567892",
                "status": "active",
                "total_deposits": Decimal("2000.00"),
                "total_bets": Decimal("3000.00"),
                "lifetime_value": Decimal("600.00"),
                "segment_id": high_value_segment.id
            },
            {
                "operator_id": operator2.id,
                "external_player_id": "PLAYER004",
                "email": "alice.brown@example.com",
                "first_name": "Alice",
                "last_name": "Brown",
                "phone": "+1234567893",
                "status": "inactive",
                "total_deposits": Decimal("500.00"),
                "total_bets": Decimal("800.00"),
                "lifetime_value": Decimal("200.00")
            },
            {
                "operator_id": operator1.id,
                "external_player_id": "PLAYER005",
                "email": "charlie.davis@example.com",
                "first_name": "Charlie",
                "last_name": "Davis",
                "phone": "+1234567894",
                "status": "active",
                "total_deposits": Decimal("3000.00"),
                "total_bets": Decimal("5000.00"),
                "lifetime_value": Decimal("900.00")
            }
        ]
        
        players = []
        for player_data in players_data:
            player = Player(
                registration_date=datetime.now() - timedelta(days=30 if player_data["status"] == "active" else 5),
                last_active_date=datetime.now() - timedelta(days=1 if player_data["status"] == "active" else 15),
                **{k: v for k, v in player_data.items() if k != "operator_id"}
            )
            player.operator_id = player_data["operator_id"]
            db.add(player)
            players.append(player)
        
        db.commit()
        for player in players:
            db.refresh(player)
        print(f"✅ Created {len(players)} players")
        
        # 4. Create Events
        print("Creating events...")
        event_types = ["registration", "deposit", "bet", "withdrawal", "game_play"]
        for player in players[:3]:  # Events for first 3 players
            for i, event_type in enumerate(event_types):
                event = Event(
                    player_id=player.id,
                    operator_id=player.operator_id,
                    event_type=event_type,
                    event_data={
                        "amount": 100 * (i + 1) if event_type in ["deposit", "bet"] else None
                    },
                    source_utm="google",
                    medium_utm="cpc",
                    campaign_utm="summer_promo",
                    timestamp=player.registration_date + timedelta(days=i)
                )
                db.add(event)
        db.commit()
        print("✅ Created events")
        
        # 5. Create Campaigns
        print("Creating campaigns...")
        campaigns_data = [
            {
                "operator_id": operator1.id,
                "name": "Welcome Campaign",
                "description": "Welcome new players",
                "campaign_type": "email",
                "trigger_type": "event_based",
                "target_segment_id": new_players_segment.id,
                "status": "active"
            },
            {
                "operator_id": operator1.id,
                "name": "High Value Player Bonus",
                "description": "Bonus for high value players",
                "campaign_type": "email",
                "trigger_type": "scheduled",
                "target_segment_id": high_value_segment.id,
                "status": "active"
            },
            {
                "operator_id": operator1.id,
                "name": "Deposit Reminder",
                "description": "Remind inactive players to deposit",
                "campaign_type": "sms",
                "trigger_type": "event_based",
                "status": "draft"
            }
        ]
        
        campaigns = []
        for campaign_data in campaigns_data:
            campaign = Campaign(**campaign_data)
            db.add(campaign)
            campaigns.append(campaign)
        
        db.commit()
        for campaign in campaigns:
            db.refresh(campaign)
        print(f"✅ Created {len(campaigns)} campaigns")
        
        # Update segment player counts
        high_value_segment.player_count = len([p for p in players if p.segment_id == high_value_segment.id])
        new_players_segment.player_count = len([p for p in players if p.segment_id == new_players_segment.id])
        db.commit()
        
        print("\n🎉 Sample data seeded successfully!")
        print(f"\nSummary:")
        print(f"  - Operators: 2")
        print(f"  - Segments: 2")
        print(f"  - Players: {len(players)}")
        print(f"  - Events: {len(event_types) * 3}")
        print(f"  - Campaigns: {len(campaigns)}")
        print(f"\n✅ Database is ready for testing!")
        
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding sample data: {e}")
        print(f"❌ Error seeding sample data: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Promotional Marketing Engine - Sample Data Seeder")
    print("=" * 60)
    print()
    
    # Seed data (assumes database is already initialized)
    success = seed_sample_data()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Setup complete! You can now:")
        print("  1. Start backend: uvicorn app.main:app --reload")
        print("  2. Start frontend: cd ../frontend && python3 -m http.server 8080")
        print("  3. Visit: http://localhost:8080")
        print("=" * 60)
    
    sys.exit(0 if success else 1)

