"""
Segmentation Service
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from app.models.player import Player
from app.models.segment import Segment
from app.models.event import Event
from app.utils.logger import logger


def _player_matches_criteria(player: Player, criteria: Dict[str, Any]) -> bool:
    """Check if player matches segment criteria."""
    if not criteria:
        return True
    if "status" in criteria:
        if isinstance(criteria["status"], list):
            if player.status not in criteria["status"]:
                return False
        elif player.status != criteria["status"]:
            return False
    ltv = float(player.lifetime_value or 0)
    if "ltv_min" in criteria and ltv < float(criteria["ltv_min"]):
        return False
    if "ltv_max" in criteria and ltv > float(criteria["ltv_max"]):
        return False
    return True


class SegmentationService:
    """Service for player segmentation"""
    
    @staticmethod
    def update_player_status(db: Session, player_id: int) -> None:
        """Update player status based on activity"""
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return
        
        # Check last activity
        if not player.last_active_date:
            player.status = "new"
        else:
            days_since_active = (datetime.now() - player.last_active_date).days
            
            if days_since_active < 7:
                player.status = "active"
            elif days_since_active < 30:
                player.status = "inactive"
            else:
                player.status = "churned"
        
        db.commit()
    
    @staticmethod
    def get_players_by_segment(
        db: Session,
        segment_id: int,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Player]:
        """Get players in a segment"""
        return db.query(Player).filter(
            Player.segment_id == segment_id
        ).limit(limit).offset(offset).all()
    
    @staticmethod
    def create_rfm_segments(db: Session, operator_id: int) -> List[Segment]:
        """Create RFM-based segments"""
        # This is a simplified version - full RFM would calculate Recency, Frequency, Monetary
        segments = []
        
        # High Value Active Players
        high_value = Segment(
            operator_id=operator_id,
            name="High Value Active",
            description="High LTV, active players",
            segment_type="rfm",
            criteria={
                "status": "active",
                "ltv_min": 1000,
                "days_since_active_max": 7
            }
        )
        db.add(high_value)
        segments.append(high_value)
        
        # At Risk Players
        at_risk = Segment(
            operator_id=operator_id,
            name="At Risk",
            description="Players showing churn signals",
            segment_type="predictive",
            criteria={
                "status": "inactive",
                "days_since_active_min": 7,
                "days_since_active_max": 30
            }
        )
        db.add(at_risk)
        segments.append(at_risk)
        
        # New Players
        new_players = Segment(
            operator_id=operator_id,
            name="New Players",
            description="Recently registered players",
            segment_type="behavioral",
            criteria={
                "status": "new",
                "days_since_registration_max": 7
            }
        )
        db.add(new_players)
        segments.append(new_players)
        
        db.commit()
        return segments

    @staticmethod
    def assign_players_to_segment(
        db: Session,
        operator_id: int,
        segment_id: int,
        criteria: Dict[str, Any],
        only_unassigned: bool = False,
    ) -> int:
        """Assign players matching criteria to this segment. Returns count assigned."""
        q = db.query(Player).filter(Player.operator_id == operator_id)
        if only_unassigned:
            q = q.filter(Player.segment_id.is_(None))
        players = q.all()
        segment = db.query(Segment).filter(Segment.id == segment_id).first()
        if not segment:
            return 0
        count = 0
        for p in players:
            if _player_matches_criteria(p, criteria or {}):
                p.segment_id = segment_id
                count += 1
        if count > 0:
            segment.player_count = count
        db.commit()
        db.refresh(segment)
        return count

    @staticmethod
    def get_player_aggregates(db: Session, operator_id: int) -> Dict[str, Any]:
        """Get aggregate stats for players (for AI segment suggestions)."""
        players = db.query(Player).filter(Player.operator_id == operator_id).all()
        if not players:
            return {"total": 0, "by_status": {}, "ltv_buckets": []}
        by_status = {}
        ltv_values = []
        for p in players:
            by_status[p.status] = by_status.get(p.status, 0) + 1
            ltv_values.append(float(p.lifetime_value or 0))
        ltv_values.sort()
        n = len(ltv_values)
        buckets = [
            {"name": "0-25%", "min": 0, "max": ltv_values[int(n * 0.25)] if n else 0, "count": max(1, n // 4)},
            {"name": "25-50%", "min": ltv_values[int(n * 0.25)] if n else 0, "max": ltv_values[int(n * 0.5)] if n else 0, "count": max(1, n // 4)},
            {"name": "50-75%", "min": ltv_values[int(n * 0.5)] if n else 0, "max": ltv_values[int(n * 0.75)] if n else 0, "count": max(1, n // 4)},
            {"name": "75-100%", "min": ltv_values[int(n * 0.75)] if n else 0, "max": ltv_values[-1] if n else 0, "count": n - 3 * max(1, n // 4)},
        ]
        return {
            "total": len(players),
            "by_status": by_status,
            "ltv_min": min(ltv_values) if ltv_values else 0,
            "ltv_max": max(ltv_values) if ltv_values else 0,
            "ltv_median": ltv_values[int(n * 0.5)] if n else 0,
        }

