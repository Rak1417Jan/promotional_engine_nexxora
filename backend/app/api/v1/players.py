"""
Player API Endpoints
"""
import random
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.api.v1.auth import get_current_user
from app.models.operator_user import OperatorUser
from app.schemas.player import PlayerCreate, PlayerUpdate, PlayerResponse, PaginatedPlayersResponse
from app.models.player import Player
from app.models.operator import Operator
from app.utils.logger import logger

router = APIRouter(prefix="/players", tags=["players"])

# Sample data for bulk seed
FIRST_NAMES = (
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Lisa", "Daniel", "Nancy",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
)
LAST_NAMES = (
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
)
DOMAINS = ("example.com", "mail.com", "test.org", "demo.net", "sample.io")
STATUSES = ("new", "active", "active", "active", "inactive")


@router.post("/", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
async def create_player(
    player: PlayerCreate,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new player (operator_id from token)."""
    try:
        operator_id = current_user.operator_id
        if getattr(player, "operator_id", None) is not None and player.operator_id != operator_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        # Verify operator exists
        operator = db.query(Operator).filter(Operator.id == operator_id).first()
        if not operator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Operator not found"
            )
        
        # Check if player already exists
        if player.external_player_id:
            existing = db.query(Player).filter(
                Player.operator_id == operator_id,
                Player.external_player_id == player.external_player_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Player already exists"
                )
        
        db_player = Player(
            operator_id=operator_id,
            external_player_id=player.external_player_id,
            email=player.email,
            phone=player.phone,
            first_name=player.first_name,
            last_name=player.last_name,
            registration_date=player.registration_date,
            status="new"
        )
        db.add(db_player)
        db.commit()
        db.refresh(db_player)
        
        logger.info("Player created", player_id=db_player.id, operator_id=operator_id)
        return db_player
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Error creating player", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating player"
        )


@router.post("/seed-sample")
async def seed_sample_players(
    count: int = Query(1000, ge=1, le=2000, description="Number of sample players to create"),
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create sample players for the current operator (for demo/testing)."""
    operator_id = current_user.operator_id
    operator = db.query(Operator).filter(Operator.id == operator_id).first()
    if not operator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operator not found")

    created = 0
    base_ext_id = int(datetime.utcnow().timestamp() * 1000)
    try:
        for i in range(count):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            domain = random.choice(DOMAINS)
            email = f"{first.lower()}.{last.lower()}.{base_ext_id + i}@{domain}"
            external_id = f"ext_{operator_id}_{base_ext_id + i}"
            status_val = random.choice(STATUSES)
            reg_days_ago = random.randint(1, 365)
            registration_date = datetime.utcnow() - timedelta(days=reg_days_ago)
            player = Player(
                operator_id=operator_id,
                external_player_id=external_id,
                email=email,
                phone=f"+1{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}" if random.random() > 0.3 else None,
                first_name=first,
                last_name=last,
                registration_date=registration_date,
                status=status_val,
                total_deposits=Decimal(random.randint(0, 50000) / 100),
                total_bets=Decimal(random.randint(0, 30000) / 100),
                lifetime_value=Decimal(random.randint(-500, 10000) / 100),
            )
            db.add(player)
            created += 1
            if created % 200 == 0:
                db.flush()
        db.commit()
        logger.info("Sample players seeded", operator_id=operator_id, count=created)
        return {"message": f"Created {created} sample players", "count": created}
    except Exception as e:
        db.rollback()
        logger.error("Error seeding sample players", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error seeding players: {str(e)}",
        )


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(
    player_id: int,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a player by ID (tenant-scoped)."""
    player = db.query(Player).filter(
        Player.id == player_id,
        Player.operator_id == current_user.operator_id
    ).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    return player


@router.put("/{player_id}", response_model=PlayerResponse)
async def update_player(
    player_id: int,
    player_update: PlayerUpdate,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a player (tenant-scoped)."""
    player = db.query(Player).filter(
        Player.id == player_id,
        Player.operator_id == current_user.operator_id
    ).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    update_data = player_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(player, field, value)
    db.commit()
    db.refresh(player)
    return player


@router.get("/", response_model=PaginatedPlayersResponse)
async def list_players(
    operator_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List players with pagination (tenant-scoped when authenticated)."""
    query = db.query(Player)
    effective_operator_id = operator_id if operator_id is not None else current_user.operator_id
    if effective_operator_id is not None:
        query = query.filter(Player.operator_id == effective_operator_id)
    if status:
        query = query.filter(Player.status == status)
    total = query.count()
    players = query.order_by(Player.id).limit(limit).offset(offset).all()
    return PaginatedPlayersResponse(items=players, total=total, limit=limit, offset=offset)

