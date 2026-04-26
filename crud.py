from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from database import DataEntry, RedundancyLog, generate_content_hash
from schemas import DataEntryCreate, DataEntryResponse, StatisticsResponse
from redundancy_detector import RedundancyDetector
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CRUDOperations:
    def __init__(self):
        self.detector = RedundancyDetector()
    
    def create_data_entry(self, entry: DataEntryCreate, db: Session, force_add: bool = False) -> tuple[Optional[DataEntry], str]:
        """Create a new data entry with redundancy checking"""
        
        # Perform redundancy check
        redundancy_result = self.detector.classify_redundancy(entry.content, entry.data_type, db)
        
        # Log the redundancy check
        self._log_redundancy_check(entry, redundancy_result, db)
        
        # Determine if we should add the entry
        should_add = force_add or not redundancy_result.is_duplicate
        
        if should_add:
            try:
                # For force add with exact duplicates, modify hash slightly
                content_hash = generate_content_hash(entry.content)
                if force_add and redundancy_result.similarity_score == 1.0:
                    # Add a suffix to make hash unique for force-added duplicates
                    import time
                    content_hash = generate_content_hash(entry.content + f"_force_{int(time.time())}")
                
                # Create new entry
                db_entry = DataEntry(
                    content=entry.content,
                    content_hash=content_hash,
                    data_type=entry.data_type,
                    source=entry.source,
                    similarity_score=redundancy_result.similarity_score,
                    is_duplicate=force_add and redundancy_result.similarity_score == 1.0,  # Mark as duplicate if force added exact duplicate
                    is_false_positive=redundancy_result.is_false_positive
                )
                
                db.add(db_entry)
                db.commit()
                db.refresh(db_entry)
                
                logger.info(f"Successfully added new entry: {db_entry.id}")
                return db_entry, "Entry added successfully"
                
            except Exception as e:
                db.rollback()
                logger.error(f"Error adding entry: {str(e)}")
                return None, f"Error adding entry: {str(e)}"
        else:
            logger.info(f"Rejected duplicate entry: {redundancy_result.recommendation}")
            return None, redundancy_result.recommendation
    
    def get_data_entry(self, entry_id: int, db: Session) -> Optional[DataEntry]:
        """Get a specific data entry by ID"""
        return db.query(DataEntry).filter(DataEntry.id == entry_id).first()
    
    def get_data_entries(self, db: Session, skip: int = 0, limit: int = 100) -> List[DataEntry]:
        """Get all data entries with pagination"""
        return db.query(DataEntry).offset(skip).limit(limit).all()
    
    def get_unique_entries(self, db: Session, skip: int = 0, limit: int = 100) -> List[DataEntry]:
        """Get only unique (non-duplicate) entries"""
        return db.query(DataEntry).filter(
            and_(DataEntry.is_duplicate == False, DataEntry.is_false_positive == False)
        ).offset(skip).limit(limit).all()
    
    def search_entries(self, db: Session, query: str, data_type: Optional[str] = None) -> List[DataEntry]:
        """Search entries by content"""
        search_filter = DataEntry.content.contains(query)
        if data_type:
            search_filter = and_(search_filter, DataEntry.data_type == data_type)
        
        return db.query(DataEntry).filter(search_filter).all()
    
    def update_entry(self, db: Session, entry_id: int, entry_update: dict) -> Optional[DataEntry]:
        """Update a data entry"""
        db_entry = db.query(DataEntry).filter(DataEntry.id == entry_id).first()
        if not db_entry:
            return None
        
        for field, value in entry_update.items():
            if hasattr(db_entry, field):
                setattr(db_entry, field, value)
        
        if 'content' in entry_update:
            new_hash = generate_content_hash(entry_update['content'])
            # Check if new hash conflicts with existing entries (excluding current entry)
            existing = db.query(DataEntry).filter(
                DataEntry.content_hash == new_hash,
                DataEntry.id != entry_id
            ).first()
            
            if existing:
                # Add timestamp to make hash unique
                import time
                new_hash = generate_content_hash(entry_update['content'] + f"_updated_{int(time.time())}")
            
            db_entry.content_hash = new_hash
        
        db_entry.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_entry)
        return db_entry
    
    def delete_entry(self, db: Session, entry_id: int) -> bool:
        """Delete a data entry"""
        db_entry = db.query(DataEntry).filter(DataEntry.id == entry_id).first()
        if not db_entry:
            return False
        
        db.delete(db_entry)
        db.commit()
        return True
    
    def mark_as_duplicate(self, db: Session, entry_id: int, original_id: int, similarity_score: float) -> bool:
        """Mark an entry as duplicate"""
        db_entry = db.query(DataEntry).filter(DataEntry.id == entry_id).first()
        if not db_entry:
            return False
        
        db_entry.is_duplicate = True
        db_entry.similarity_score = similarity_score
        db.commit()
        
        # Log the action
        log_entry = RedundancyLog(
            original_entry_id=original_id,
            duplicate_entry_id=entry_id,
            similarity_score=similarity_score,
            detection_method="manual",
            action_taken="marked_as_duplicate"
        )
        db.add(log_entry)
        db.commit()
        
        return True
    
    def mark_as_false_positive(self, db: Session, entry_id: int) -> bool:
        """Mark an entry as false positive"""
        db_entry = db.query(DataEntry).filter(DataEntry.id == entry_id).first()
        if not db_entry:
            return False
        
        db_entry.is_false_positive = True
        db_entry.is_duplicate = False
        db.commit()
        return True
    
    def get_statistics(self, db: Session) -> StatisticsResponse:
        """Get database statistics"""
        total_entries = db.query(DataEntry).count()
        unique_entries = db.query(DataEntry).filter(
            and_(DataEntry.is_duplicate == False, DataEntry.is_false_positive == False)
        ).count()
        duplicates_found = db.query(DataEntry).filter(DataEntry.is_duplicate == True).count()
        false_positives = db.query(DataEntry).filter(DataEntry.is_false_positive == True).count()
        
        # Data type distribution
        type_distribution = db.query(
            DataEntry.data_type,
            func.count(DataEntry.id).label('count')
        ).group_by(DataEntry.data_type).all()
        
        data_type_distribution = {item[0]: item[1] for item in type_distribution}
        
        return StatisticsResponse(
            total_entries=total_entries,
            unique_entries=unique_entries,
            duplicates_found=duplicates_found,
            false_positives=false_positives,
            data_type_distribution=data_type_distribution
        )
    
    def validate_entry(self, db: Session, entry: DataEntryCreate) -> tuple[bool, str, Optional[dict]]:
        """Validate if an entry can be added"""
        redundancy_result = self.detector.classify_redundancy(entry.content, entry.data_type, db)
        
        can_add = not redundancy_result.is_duplicate
        message = redundancy_result.recommendation
        
        return can_add, message, redundancy_result.dict()
    
    def _log_redundancy_check(self, entry: DataEntryCreate, result, db: Session):
        """Log redundancy check results"""
        try:
            log_entry = RedundancyLog(
                original_entry_id=0,  # Will be updated if entry is added
                duplicate_entry_id=None,
                similarity_score=result.similarity_score,
                detection_method="automated",
                action_taken="checked"
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            logger.error(f"Error logging redundancy check: {str(e)}")

# Create a singleton instance
crud = CRUDOperations()
