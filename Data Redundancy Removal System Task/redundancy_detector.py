from typing import List, Tuple, Optional
from thefuzz import fuzz
import re
from database import DataEntry, SessionLocal, generate_content_hash
from schemas import DataEntryResponse, RedundancyCheckResult

class RedundancyDetector:
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s]', '', text)
        return text
    
    def check_exact_duplicate(self, content: str, db) -> Optional[DataEntry]:
        """Check for exact duplicates using content hash"""
        content_hash = generate_content_hash(content)
        return db.query(DataEntry).filter(DataEntry.content_hash == content_hash).first()
    
    def check_similar_content(self, content: str, data_type: str, db) -> List[Tuple[DataEntry, float]]:
        """Check for similar content using fuzzy matching"""
        normalized_content = self.normalize_text(content)
        
        similar_entries = []
        existing_entries = db.query(DataEntry).filter(
            DataEntry.data_type == data_type,
            DataEntry.is_duplicate == False,
            DataEntry.is_false_positive == False
        ).all()
        
        for entry in existing_entries:
            normalized_entry = self.normalize_text(entry.content)
            
            # Calculate similarity using multiple methods
            ratio = fuzz.ratio(normalized_content, normalized_entry) / 100.0
            partial_ratio = fuzz.partial_ratio(normalized_content, normalized_entry) / 100.0
            token_sort_ratio = fuzz.token_sort_ratio(normalized_content, normalized_entry) / 100.0
            
            # Use the highest similarity score
            max_similarity = max(ratio, partial_ratio, token_sort_ratio)
            
            if max_similarity >= self.similarity_threshold:
                similar_entries.append((entry, max_similarity))
        
        # Sort by similarity score (highest first)
        similar_entries.sort(key=lambda x: x[1], reverse=True)
        return similar_entries
    
    def classify_redundancy(self, content: str, data_type: str, db) -> RedundancyCheckResult:
        """Classify data as redundant or false positive"""
        
        # Check for exact duplicate first
        exact_duplicate = self.check_exact_duplicate(content, db)
        if exact_duplicate:
            return RedundancyCheckResult(
                is_duplicate=True,
                is_false_positive=False,
                similarity_score=1.0,
                matched_entries=[DataEntryResponse.from_orm(exact_duplicate)],
                recommendation="Exact duplicate found. Reject this entry."
            )
        
        # Check for similar content
        similar_entries = self.check_similar_content(content, data_type, db)
        
        if similar_entries:
            # Check if it might be a false positive
            top_match, similarity = similar_entries[0]
            
            # False positive heuristics
            is_false_positive = self._is_likely_false_positive(content, top_match.content, similarity)
            
            recommendation = "Similar content found. "
            if is_false_positive:
                recommendation += "Likely a false positive. Consider adding this entry."
            else:
                recommendation += "High probability of redundancy. Reject this entry."
            
            return RedundancyCheckResult(
                is_duplicate=not is_false_positive,
                is_false_positive=is_false_positive,
                similarity_score=similarity,
                matched_entries=[DataEntryResponse.from_orm(entry) for entry, _ in similar_entries[:3]],
                recommendation=recommendation
            )
        
        return RedundancyCheckResult(
            is_duplicate=False,
            is_false_positive=False,
            similarity_score=0.0,
            matched_entries=[],
            recommendation="No redundancy detected. Safe to add this entry."
        )
    
    def _is_likely_false_positive(self, new_content: str, existing_content: str, similarity: float) -> bool:
        """Heuristics to determine if similar content is likely a false positive"""
        
        # If similarity is very high, it's probably not a false positive
        if similarity > 0.95:
            return False
        
        # If similarity is just above threshold, it might be a false positive
        if similarity < 0.85:
            return True
        
        # Check length difference
        length_diff = abs(len(new_content) - len(existing_content)) / max(len(new_content), len(existing_content))
        if length_diff > 0.3:  # 30% length difference
            return True
        
        # Check for common patterns that might cause false positives
        new_words = set(new_content.lower().split())
        existing_words = set(existing_content.lower().split())
        
        # If most words are different despite high similarity, it might be a false positive
        common_words = new_words.intersection(existing_words)
        total_unique_words = new_words.union(existing_words)
        
        if len(common_words) / len(total_unique_words) < 0.6:
            return True
        
        return False
