"""
Insights API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.database import get_db
from app.api.v1.auth import get_current_user
from app.models.operator_user import OperatorUser
from app.services.ml_service import MLService
from app.ml.openai_service import OpenAIService
from app.utils.logger import logger
from datetime import datetime

router = APIRouter(prefix="/insights", tags=["insights"])

# Initialize OpenAI service if enabled
try:
    from app.config import settings
    if settings.ENABLE_OPENAI and settings.OPENAI_API_KEY:
        openai_service = OpenAIService()
    else:
        openai_service = None
except Exception:
    openai_service = None


def _features_from_player_row(player) -> Dict[str, Any]:
    """Build feature dict from PostgreSQL Player row for insights."""
    from datetime import datetime
    reg = getattr(player, "registration_date", None) or getattr(player, "created_at", None)
    last_active = getattr(player, "last_active_date", None)
    reg_days = (datetime.utcnow() - reg).days if reg else 0
    days_inactive = (datetime.utcnow() - last_active).days if last_active else 999
    return {
        "total_deposits": float(getattr(player, "total_deposits", 0) or 0),
        "total_withdrawals": float(getattr(player, "total_withdrawals", 0) or 0),
        "total_bets": float(getattr(player, "total_bets", 0) or 0),
        "registration_days_ago": reg_days,
        "days_since_last_activity": days_inactive,
    }


@router.get("/players/{player_id}")
async def get_player_insights(
    player_id: str,
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get insights for a specific player (by id or external_player_id)."""
    from app.models.player import Player

    try:
        operator_id = current_user.operator_id

        # Resolve player: try by numeric id, then by external_player_id
        player = None
        try:
            pid = int(player_id)
            player = db.query(Player).filter(
                Player.id == pid,
                Player.operator_id == operator_id,
            ).first()
        except ValueError:
            pass
        if not player:
            player = db.query(Player).filter(
                Player.operator_id == operator_id,
                Player.external_player_id == player_id,
            ).first()
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found"
            )

        # Use string id for cache/key consistency
        resolved_id = str(player.id)
        features = MLService.extract_features_from_player(operator_id, resolved_id)
        if not features:
            features = _features_from_player_row(player)
        
        # Check cache first (use resolved player id)
        churn_prediction = MLService.get_cached_prediction(db, operator_id, resolved_id, "churn")
        ltv_prediction = MLService.get_cached_prediction(db, operator_id, resolved_id, "ltv")

        # Generate predictions if not cached
        if not churn_prediction:
            churn_prediction = MLService.predict_churn(db, operator_id, resolved_id, features)

        if not ltv_prediction:
            ltv_prediction = MLService.predict_ltv(db, operator_id, resolved_id, features)
        
        # Generate recommendations
        recommendations = []
        if churn_prediction.get("churn_risk_7d", 0) > 0.7:
            recommendations.append({
                "type": "campaign",
                "action": "Send win-back email campaign",
                "priority": "high",
                "reason": "High churn risk detected"
            })
        
        if ltv_prediction.get("ltv_prediction", 0) > 5000:
            recommendations.append({
                "type": "segment",
                "action": "Add to high-value player segment",
                "priority": "medium",
                "reason": "High predicted lifetime value"
            })
        
        return {
            "player_id": resolved_id,
            "churn_risk": {
                "7_day": churn_prediction.get("churn_risk_7d", 0),
                "30_day": churn_prediction.get("churn_risk_30d", 0),
                "confidence": churn_prediction.get("confidence", 0)
            },
            "ltv_prediction": {
                "value": ltv_prediction.get("ltv_prediction", 0),
                "confidence": ltv_prediction.get("confidence", 0)
            },
            "recommendations": recommendations,
            "features_used": features
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting player insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating insights: {str(e)}"
        )


@router.get("/campaigns/recommendations")
async def get_campaign_recommendations(
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get campaign recommendations"""
    try:
        operator_id = current_user.operator_id
        
        # TODO: Analyze player data and generate recommendations
        # For now, return mock recommendations
        
        recommendations = [
            {
                "campaign_type": "email",
                "target_segment": "inactive_players",
                "timing": "optimal",
                "expected_engagement": 0.25,
                "reason": "High number of inactive players detected"
            },
            {
                "campaign_type": "sms",
                "target_segment": "high_value_players",
                "timing": "optimal",
                "expected_engagement": 0.40,
                "reason": "High-value players respond well to SMS"
            }
        ]
        
        return {
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting campaign recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.get("/business")
async def get_business_insights(
    current_user: OperatorUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get business intelligence insights"""
    try:
        operator_id = current_user.operator_id
        
        # TODO: Generate actual business insights from data
        # For now, return mock insights
        
        insights = {
            "revenue_forecast": {
                "next_30_days": 50000,
                "next_90_days": 150000,
                "confidence": 0.75
            },
            "player_acquisition_cost": {
                "by_channel": {
                    "google": 25.50,
                    "facebook": 30.00,
                    "organic": 5.00
                }
            },
            "retention_rate": {
                "7_day": 0.65,
                "30_day": 0.45,
                "trend": "improving"
            }
        }
        
        # Generate natural language summary using LLM (OpenAI or Groq)
        if openai_service and hasattr(openai_service, 'generate_insight_summary'):
            try:
                summary = openai_service.generate_insight_summary(insights)
                insights["summary"] = summary
            except Exception as e:
                logger.warning(f"Could not generate AI summary: {e}")
        
        return insights
        
    except Exception as e:
        logger.error(f"Error getting business insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating business insights: {str(e)}"
        )
