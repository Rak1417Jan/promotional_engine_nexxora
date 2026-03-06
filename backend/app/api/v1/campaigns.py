"""
Campaign API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.api.v1.auth import get_current_user
from app.models.operator_user import OperatorUser
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse
from app.models.campaign import Campaign
from app.services.campaign_service import CampaignService
from app.ml.openai_service import OpenAIService
from app.utils.logger import logger

router = APIRouter(prefix="/campaigns", tags=["campaigns"])
openai_service = OpenAIService()


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign: CampaignCreate,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new campaign (operator_id from token)."""
    try:
        campaign_data = campaign.dict()
        campaign_data["operator_id"] = current_user.operator_id
        db_campaign = CampaignService.create_campaign(
            db=db,
            campaign_data=campaign_data,
            operator_id=current_user.operator_id
        )
        logger.info("Campaign created", campaign_id=db_campaign.id, name=campaign.name)
        return db_campaign
    except Exception as e:
        db.rollback()
        logger.error("Error creating campaign", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating campaign"
        )


@router.post("/ai-generate", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_ai_campaign(
    objective: str,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a campaign from natural language objective using AI. Also creates a target segment from AI and assigns players."""
    from app.models.segment import Segment
    from app.models.player import Player
    from app.services.segmentation_service import SegmentationService

    try:
        generated_config = openai_service.generate_campaign_from_objective(objective)
        operator_id = current_user.operator_id
        target_segment_id = None

        # Ask AI for segment criteria to target for this campaign
        try:
            seg_prompt = f"""Campaign objective: {objective}
Target segment suggestion from campaign: {generated_config.get('target_segment', '')}

Return a JSON object with segment for this campaign: name, description, criteria.
criteria can use: status (string or array: active, inactive, new), ltv_min (number), ltv_max (number).
Example: {{"name": "Active players", "description": "Target active users", "criteria": {{"status": "active"}}}}
Return only the JSON object."""
            seg_content = openai_service.llm_service.generate_text(
                prompt=seg_prompt,
                system_prompt="You are a segmentation expert. Return only valid JSON.",
                temperature=0.4,
                max_tokens=300,
            )
            import json
            import re
            if "```" in seg_content:
                seg_content = re.sub(r"```\w*\n?", "", seg_content).strip()
            seg_obj = json.loads(seg_content) if isinstance(seg_content, str) else seg_content
            if isinstance(seg_obj, list):
                seg_obj = seg_obj[0] if seg_obj else {}
            name = seg_obj.get("name") or "Campaign target"
            description = seg_obj.get("description") or objective[:200]
            criteria = seg_obj.get("criteria") or {"status": "active"}
            seg = Segment(
                operator_id=operator_id,
                name=name,
                description=description,
                segment_type="behavioral",
                criteria=criteria,
                player_count=0,
            )
            db.add(seg)
            db.flush()
            count = SegmentationService.assign_players_to_segment(db, operator_id, seg.id, criteria, only_unassigned=False)
            seg.player_count = count
            target_segment_id = seg.id
            db.commit()
            db.refresh(seg)
        except Exception as seg_err:
            logger.warning("AI segment creation failed, campaign will have no segment", error=str(seg_err))
            if target_segment_id is None:
                db.rollback()

        campaign_data = {
            "name": generated_config.get("name", "AI Generated Campaign"),
            "description": generated_config.get("description", objective),
            "campaign_type": generated_config.get("campaign_type", "email"),
            "trigger_type": "ai_optimized",
            "ai_generated": True,
            "ai_objective": objective,
            "operator_id": operator_id,
            "target_segment_id": target_segment_id,
        }
        db_campaign = CampaignService.create_campaign(
            db=db,
            campaign_data=campaign_data,
            operator_id=operator_id
        )
        logger.info("AI campaign created", campaign_id=db_campaign.id, target_segment_id=target_segment_id)
        return db_campaign
    except Exception as e:
        db.rollback()
        logger.error("Error creating AI campaign", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating AI campaign"
        )


@router.get("/{campaign_id}/details")
async def get_campaign_details(
    campaign_id: int,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get full campaign details: campaign, target segment, target players list, and analytics."""
    from app.models.segment import Segment
    from app.models.player import Player

    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.operator_id == current_user.operator_id
    ).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    segment = None
    if campaign.target_segment_id:
        seg_row = db.query(Segment).filter(
            Segment.id == campaign.target_segment_id,
            Segment.operator_id == current_user.operator_id,
        ).first()
        if seg_row:
            segment = {
                "id": seg_row.id,
                "name": seg_row.name,
                "description": seg_row.description,
                "segment_type": seg_row.segment_type,
                "criteria": seg_row.criteria,
                "player_count": seg_row.player_count,
            }

    targets = CampaignService.get_campaign_targets(db, campaign_id)
    target_players = [
        {
            "id": p.id,
            "email": p.email,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "status": p.status,
            "lifetime_value": float(p.lifetime_value or 0),
        }
        for p in (targets[:500])
    ]

    analytics = CampaignService.get_campaign_analytics(db, campaign_id)

    return {
        "campaign": {
            "id": campaign.id,
            "name": campaign.name,
            "description": campaign.description,
            "campaign_type": campaign.campaign_type,
            "status": campaign.status,
            "target_segment_id": campaign.target_segment_id,
        },
        "segment": segment,
        "target_players": target_players,
        "target_count": len(targets),
        "analytics": analytics,
    }


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a campaign by ID (tenant-scoped)."""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.operator_id == current_user.operator_id
    ).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_update: CampaignUpdate,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a campaign (tenant-scoped)."""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.operator_id == current_user.operator_id
    ).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    update_data = campaign_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/execute")
async def execute_campaign(
    campaign_id: int,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute a campaign (tenant-scoped)."""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.operator_id == current_user.operator_id
    ).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    try:
        execution_count = CampaignService.execute_campaign(db, campaign_id)
        return {"message": "Campaign execution started", "executions_created": execution_count}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Error executing campaign", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error executing campaign"
        )


@router.get("/", response_model=List[CampaignResponse])
async def list_campaigns(
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List campaigns for current operator."""
    query = db.query(Campaign).filter(Campaign.operator_id == current_user.operator_id)
    if status:
        query = query.filter(Campaign.status == status)
    campaigns = query.limit(limit).offset(offset).all()
    return campaigns


@router.get("/{campaign_id}/analytics")
async def get_campaign_analytics(
    campaign_id: int,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get campaign analytics (tenant-scoped)."""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.operator_id == current_user.operator_id
    ).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    try:
        return CampaignService.get_campaign_analytics(db, campaign_id)
    except Exception as e:
        logger.error("Error getting campaign analytics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting campaign analytics"
        )

