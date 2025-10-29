from typing import Dict, Any, List
from pathlib import Path
import json
from datetime import datetime

class FeedbackLearner:
    def __init__(self):
        self.feedback_dir = Path("storage/feedback")
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_file = self.feedback_dir / "feedback.jsonl"
    
    def store_feedback(self, query: str, answer: str, rating: int, user_id: str, comment: str = None):
        """Store feedback for continuous learning"""
        
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "query": query,
            "answer": answer,
            "rating": rating,
            "comment": comment
        }
        
        with open(self.feedback_file, 'a') as f:
            f.write(json.dumps(feedback_entry) + '\n')
    
    def get_low_rated_queries(self, threshold: int = 3) -> List[Dict[str, Any]]:
        """Get queries with low ratings for improvement"""
        
        if not self.feedback_file.exists():
            return []
        
        low_rated = []
        with open(self.feedback_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                if entry['rating'] <= threshold:
                    low_rated.append(entry)
        
        return low_rated
    
    def get_query_patterns(self) -> Dict[str, Any]:
        """Analyze feedback to find patterns"""
        
        if not self.feedback_file.exists():
            return {"total": 0, "avg_rating": 0, "common_issues": []}
        
        ratings = []
        queries = []
        
        with open(self.feedback_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                ratings.append(entry['rating'])
                queries.append(entry['query'])
        
        return {
            "total": len(ratings),
            "avg_rating": sum(ratings) / len(ratings) if ratings else 0,
            "total_queries": len(queries),
            "low_rated_count": len([r for r in ratings if r <= 3])
        }

feedback_learner = FeedbackLearner()
