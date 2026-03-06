"""
Event API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.event import EventCreate, EventResponse
from app.models.event import Event
from app.models.player import Player
from app.services.attribution_service import AttributionService
from app.services.segmentation_service import SegmentationService
from app.utils.logger import logger

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event: EventCreate,
    db: Session = Depends(get_db)
):
    """Create a new event"""
    try:
        # Verify player exists
        player = db.query(Player).filter(Player.id == event.player_id).first()
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found"
            )
        
        # Create event
        db_event = Event(
            player_id=event.player_id,
            operator_id=event.operator_id,
            event_type=event.event_type,
            event_data=event.event_data or {},
            source_utm=event.source_utm,
            medium_utm=event.medium_utm,
            campaign_utm=event.campaign_utm,
            timestamp=event.timestamp
        )
        db.add(db_event)
        
        # Update attribution if UTM parameters present
        if event.source_utm or event.medium_utm or event.campaign_utm:
            AttributionService.create_or_update_attribution(
                db=db,
                player_id=event.player_id,
                operator_id=event.operator_id,
                source=event.source_utm,
                medium=event.medium_utm,
                campaign=event.campaign_utm
            )
        
        # Update player activity
        if event.event_type in ["deposit", "bet", "game_play"]:
            from datetime import datetime
            player.last_active_date = datetime.now()
            SegmentationService.update_player_status(db, event.player_id)
        
        # Update player stats based on event type
        if event.event_type == "deposit":
            amount = event.event_data.get("amount", 0)
            if amount:
                player.total_deposits += amount
                player.lifetime_value += amount
        elif event.event_type == "withdrawal":
            amount = event.event_data.get("amount", 0)
            if amount:
                player.total_withdrawals += amount
        elif event.event_type == "bet":
            amount = event.event_data.get("amount", 0)
            if amount:
                player.total_bets += amount
        
        db.commit()
        db.refresh(db_event)
        
        logger.info("Event created", event_id=db_event.id, event_type=event.event_type)
        return db_event
        
    except Exception as e:
        db.rollback()
        logger.error("Error creating event", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating event"
        )


@router.get("/player/{player_id}", response_model=List[EventResponse])
async def get_player_events(
    player_id: int,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get events for a player"""
    events = db.query(Event).filter(
        Event.player_id == player_id
    ).order_by(Event.timestamp.desc()).limit(limit).offset(offset).all()
    
    return events


@router.get("/operator/{operator_id}", response_model=List[EventResponse])
async def get_operator_events(
    operator_id: int,
    event_type: str = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get events for an operator"""
    query = db.query(Event).filter(Event.operator_id == operator_id)
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    events = query.order_by(Event.timestamp.desc()).limit(limit).offset(offset).all()
    return events

