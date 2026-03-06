"""
Segments API Endpoints
"""
import json
import re
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.api.v1.auth import get_current_user
from app.models.operator_user import OperatorUser
from app.models.segment import Segment
from app.models.player import Player
from app.schemas.segment import SegmentCreate, SegmentResponse
from app.services.segmentation_service import SegmentationService
from app.ml.llm_service import LLMService
from app.utils.logger import logger

router = APIRouter(prefix="/segments", tags=["segments"])
llm_service = LLMService()


@router.get("/", response_model=List[SegmentResponse])
async def list_segments(
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List segments for current operator."""
    segments = (
        db.query(Segment)
        .filter(Segment.operator_id == current_user.operator_id)
        .order_by(Segment.id)
        .all()
    )
    return segments


@router.post("/", response_model=SegmentResponse, status_code=status.HTTP_201_CREATED)
async def create_segment(
    segment: SegmentCreate,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a segment."""
    seg = Segment(
        operator_id=current_user.operator_id,
        name=segment.name,
        description=segment.description,
        segment_type=segment.segment_type,
        criteria=segment.criteria or {},
    )
    db.add(seg)
    db.commit()
    db.refresh(seg)
    return seg


@router.post("/ai-generate")
async def ai_generate_segments(
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create segments from player metadata using AI. Assigns players to segments by criteria."""
    operator_id = current_user.operator_id
    aggregates = SegmentationService.get_player_aggregates(db, operator_id)
    if aggregates["total"] == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No players found. Import or add players first.",
        )

    prompt = f"""Based on this player base metadata, suggest 3 to 5 segments for marketing campaigns.
Player metadata:
- Total players: {aggregates['total']}
- By status: {aggregates.get('by_status', {})}
- LTV range: {aggregates.get('ltv_min', 0)} to {aggregates.get('ltv_max', 0)}

Respond with a JSON array of segments. Each segment must have:
- name: string
- description: string
- segment_type: one of "rfm", "behavioral", "predictive", "custom"
- criteria: object with optional keys: status (string or array), ltv_min (number), ltv_max (number)

Example criteria: {{"status": "active"}}, {{"ltv_min": 500}}, {{"status": "inactive", "ltv_min": 0}}
Return only the JSON array, no other text."""

    try:
        content = llm_service.generate_text(
            prompt=prompt,
            system_prompt="You are a marketing segmentation expert. Return only valid JSON array.",
            temperature=0.5,
            max_tokens=800,
        )
    except Exception as e:
        logger.error("LLM segment generation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service unavailable. Create segments manually.",
        )

    # Parse JSON array
    try:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        arr = json.loads(content)
        if not isinstance(arr, list):
            arr = [arr]
    except json.JSONDecodeError:
        match = re.search(r"\[[\s\S]*\]", content)
        if match:
            arr = json.loads(match.group())
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI returned invalid segment data.",
            )

    created = []
    # Reset segment_id for all players so we can reassign
    db.query(Player).filter(Player.operator_id == operator_id).update({Player.segment_id: None})
    db.commit()

    for item in arr[:10]:
        name = item.get("name") or "Unnamed"
        description = item.get("description") or ""
        segment_type = item.get("segment_type") or "custom"
        criteria = item.get("criteria") or {}
        seg = Segment(
            operator_id=operator_id,
            name=name,
            description=description,
            segment_type=segment_type,
            criteria=criteria,
            player_count=0,
        )
        db.add(seg)
        db.flush()
        count = SegmentationService.assign_players_to_segment(
            db, operator_id, seg.id, criteria, only_unassigned=True
        )
        seg.player_count = count
        created.append({"id": seg.id, "name": name, "player_count": count})

    db.commit()
    return {"message": f"Created {len(created)} segments", "segments": created}
