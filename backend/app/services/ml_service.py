"""
ML Service for Machine Learning Operations
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models.prediction import Prediction
from app.models.ml_model import MLModel
from app.services.mongodb_service import MongoDBService
from app.utils.logger import logger
from datetime import datetime, timedelta
import json


class MLService:
    """Service for ML model operations"""
    
    @staticmethod
    def extract_features_from_player(
        operator_id: int,
        player_id: str,
        collection_name: str = "players"
    ) -> Dict[str, Any]:
        """Extract features from player data in MongoDB"""
        try:
            player_doc = MongoDBService.get_document(collection_name, operator_id, player_id)
            if not player_doc:
                return {}
            
            data = player_doc.get("data", {})
            
            # Extract common features
            features = {
                "total_deposits": float(data.get("total_deposits", 0)),
                "total_withdrawals": float(data.get("total_withdrawals", 0)),
                "total_bets": float(data.get("total_bets", 0)),
                "registration_days_ago": 0,  # Calculate from registration_date
                "days_since_last_activity": 0,  # Calculate from last_activity
            }
            
            # Add custom features from data
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    features[f"custom_{key}"] = float(value)
            
            return features
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return {}
    
    @staticmethod
    def predict_churn(
        db: Session,
        operator_id: int,
        player_id: str,
        features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict churn risk for a player"""
        # TODO: Load actual ML model and make prediction
        # For now, return mock prediction
        
        # Simple heuristic-based prediction (will be replaced with actual model)
        days_inactive = features.get("days_since_last_activity", 0)
        total_deposits = features.get("total_deposits", 0)
        
        # Simple churn risk calculation
        if days_inactive > 30:
            churn_risk_7d = 0.9
            churn_risk_30d = 0.95
        elif days_inactive > 14:
            churn_risk_7d = 0.6
            churn_risk_30d = 0.8
        elif days_inactive > 7:
            churn_risk_7d = 0.3
            churn_risk_30d = 0.5
        else:
            churn_risk_7d = 0.1
            churn_risk_30d = 0.2
        
        # Adjust based on deposit amount
        if total_deposits > 1000:
            churn_risk_7d *= 0.7
            churn_risk_30d *= 0.7
        
        prediction = {
            "churn_risk_7d": round(churn_risk_7d, 4),
            "churn_risk_30d": round(churn_risk_30d, 4),
            "confidence": 0.75,
            "model_version": "v1.0"
        }
        
        # Cache prediction
        MLService._cache_prediction(
            db, operator_id, player_id, "churn", prediction
        )
        
        return prediction
    
    @staticmethod
    def predict_ltv(
        db: Session,
        operator_id: int,
        player_id: str,
        features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict lifetime value for a player"""
        # TODO: Load actual ML model and make prediction
        # For now, return mock prediction
        
        total_deposits = features.get("total_deposits", 0)
        registration_days = features.get("registration_days_ago", 1)
        
        # Simple LTV calculation (will be replaced with actual model)
        if registration_days > 0:
            daily_avg = total_deposits / registration_days
            predicted_days = 365  # Assume 1 year lifetime
            ltv_prediction = daily_avg * predicted_days
        else:
            ltv_prediction = total_deposits * 10  # Conservative estimate
        
        prediction = {
            "ltv_prediction": round(ltv_prediction, 2),
            "confidence": 0.70,
            "model_version": "v1.0"
        }
        
        # Cache prediction
        MLService._cache_prediction(
            db, operator_id, player_id, "ltv", prediction
        )
        
        return prediction
    
    @staticmethod
    def _cache_prediction(
        db: Session,
        operator_id: int,
        player_id: str,
        model_type: str,
        prediction_value: Dict[str, Any]
    ) -> None:
        """Cache prediction in database"""
        try:
            # Check if prediction exists
            existing = db.query(Prediction).filter(
                Prediction.operator_id == operator_id,
                Prediction.player_id == player_id,
                Prediction.model_type == model_type
            ).first()
            
            if existing:
                existing.prediction_value = prediction_value
                existing.confidence_score = prediction_value.get("confidence")
                existing.calculated_at = datetime.utcnow()
                existing.expires_at = datetime.utcnow() + timedelta(hours=24)
            else:
                prediction = Prediction(
                    operator_id=operator_id,
                    player_id=player_id,
                    model_type=model_type,
                    prediction_value=prediction_value,
                    confidence_score=prediction_value.get("confidence"),
                    expires_at=datetime.utcnow() + timedelta(hours=24)
                )
                db.add(prediction)
            
            db.commit()
        except Exception as e:
            logger.error(f"Error caching prediction: {e}")
            db.rollback()
    
    @staticmethod
    def get_cached_prediction(
        db: Session,
        operator_id: int,
        player_id: str,
        model_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached prediction if still valid"""
        prediction = db.query(Prediction).filter(
            Prediction.operator_id == operator_id,
            Prediction.player_id == player_id,
            Prediction.model_type == model_type,
            Prediction.expires_at > datetime.utcnow()
        ).first()
        
        if prediction:
            return prediction.prediction_value
        return None
