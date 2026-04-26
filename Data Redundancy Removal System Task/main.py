from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from database import get_db, create_tables
from crud import crud
from schemas import (
    DataEntryCreate, DataEntryResponse, ValidationResponse, 
    StatisticsResponse, RedundancyCheckResult
)
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Data Redundancy Removal System",
    description="A system that identifies and prevents redundant data from being added to the database",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    logger.info("Database tables created successfully")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Data Redundancy Removal System API",
        "version": "1.0.0",
        "endpoints": {
            "validate": "/validate",
            "add": "/add",
            "entries": "/entries",
            "search": "/search",
            "statistics": "/statistics"
        }
    }

@app.post("/validate", response_model=ValidationResponse)
async def validate_entry(
    entry: DataEntryCreate, 
    db: Session = Depends(get_db)
):
    """Validate if an entry can be added without creating redundancy"""
    try:
        can_add, message, redundancy_data = crud.validate_entry(db, entry)
        
        return ValidationResponse(
            is_valid=can_add,
            can_add=can_add,
            message=message,
            redundancy_check=redundancy_data
        )
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@app.post("/add", response_model=DataEntryResponse)
async def add_data_entry(
    entry: DataEntryCreate, 
    force_add: bool = Query(False, description="Force add even if duplicate is detected"),
    db: Session = Depends(get_db)
):
    """Add a new data entry with redundancy checking"""
    try:
        db_entry, message = crud.create_data_entry(entry, db, force_add)
        
        if db_entry is None:
            raise HTTPException(status_code=400, detail=message)
        
        return DataEntryResponse.from_orm(db_entry)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding entry: {str(e)}")

@app.get("/entries", response_model=List[DataEntryResponse])
async def get_entries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    unique_only: bool = Query(False, description="Get only unique (non-duplicate) entries"),
    db: Session = Depends(get_db)
):
    """Get data entries with pagination"""
    try:
        if unique_only:
            entries = crud.get_unique_entries(db, skip, limit)
        else:
            entries = crud.get_data_entries(db, skip, limit)
        
        return [DataEntryResponse.from_orm(entry) for entry in entries]
    except Exception as e:
        logger.error(f"Error fetching entries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching entries: {str(e)}")

@app.get("/entries/{entry_id}", response_model=DataEntryResponse)
async def get_entry(entry_id: int, db: Session = Depends(get_db)):
    """Get a specific data entry by ID"""
    try:
        entry = crud.get_data_entry(entry_id, db)
        if entry is None:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        return DataEntryResponse.from_orm(entry)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching entry: {str(e)}")

@app.get("/search", response_model=List[DataEntryResponse])
async def search_entries(
    query: str = Query(..., min_length=1),
    data_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Search entries by content"""
    try:
        entries = crud.search_entries(db, query, data_type)
        return [DataEntryResponse.from_orm(entry) for entry in entries]
    except Exception as e:
        logger.error(f"Error searching entries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching entries: {str(e)}")

@app.put("/entries/{entry_id}", response_model=DataEntryResponse)
async def update_entry(
    entry_id: int,
    entry_update: dict,
    db: Session = Depends(get_db)
):
    """Update a data entry"""
    try:
        entry = crud.update_entry(db, entry_id, entry_update)
        if entry is None:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        return DataEntryResponse.from_orm(entry)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating entry: {str(e)}")

@app.delete("/entries/{entry_id}")
async def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    """Delete a data entry"""
    try:
        success = crud.delete_entry(db, entry_id)
        if not success:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        return {"message": "Entry deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting entry: {str(e)}")

@app.post("/entries/{entry_id}/mark-duplicate")
async def mark_as_duplicate(
    entry_id: int,
    original_id: int,
    similarity_score: float,
    db: Session = Depends(get_db)
):
    """Mark an entry as duplicate"""
    try:
        success = crud.mark_as_duplicate(db, entry_id, original_id, similarity_score)
        if not success:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        return {"message": "Entry marked as duplicate successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking entry as duplicate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error marking entry as duplicate: {str(e)}")

@app.post("/entries/{entry_id}/mark-false-positive")
async def mark_as_false_positive(entry_id: int, db: Session = Depends(get_db)):
    """Mark an entry as false positive"""
    try:
        success = crud.mark_as_false_positive(db, entry_id)
        if not success:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        return {"message": "Entry marked as false positive successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking entry as false positive: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error marking entry as false positive: {str(e)}")

@app.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(db: Session = Depends(get_db)):
    """Get database statistics"""
    try:
        return crud.get_statistics(db)
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
