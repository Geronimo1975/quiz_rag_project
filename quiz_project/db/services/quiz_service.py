import random
from datetime import datetime
from django.utils import timezone
from typing import List, Dict, Any, Optional
from django.contrib.auth.models import User
from django.db.models import Avg, Count

from ..repositories.quiz_repository import QuizRepository
from quiz.models import Topic, Question, Answer, QuizSession, QuizResponse

class QuizService:
    def __init__(self):
        self.repository = QuizRepository()
    
    def get_topics(self) -> List[Topic]:
        """Get all quiz topics"""
        return self.repository.get_topics()
    
    def get_topic_by_id(self, topic_id: int) -> Optional[Topic]:
        """Get a topic by ID"""
        return self.repository.get_topic_by_id(topic_id)
    
    def get_questions_for_topic(self, topic_id: int, limit: Optional[int] = None) -> List[Question]:
        """Get questions for a topic, optionally limited"""
        return self.repository.get_questions_for_topic(topic_id, limit)
    
    def start_quiz_session(self, user_id: int, topic_id: int, num_questions: int = 10) -> QuizSession:
        """Start a new quiz session"""
        return self.repository.start_quiz_session(user_id, topic_id, num_questions)
    
    def get_session_by_id(self, session_id: int) -> Optional[QuizSession]:
        """Get quiz session by ID"""
        return self.repository.get_session_by_id(session_id)
    
    def get_user_sessions(self, user_id: int, topic_id: Optional[int] = None) -> List[QuizSession]:
        """Get quiz sessions for a user"""
        return self.repository.get_user_sessions(user_id, topic_id)
    
    def record_response(self, session_id: int, question_id: int, answer_id: Optional[int] = None) -> QuizResponse:
        """Record a user's response to a question"""
        return self.repository.record_response(session_id, question_id, answer_id)
    
    def complete_session(self, session_id: int) -> QuizSession:
        """Mark a quiz session as completed and calculate score"""
        return self.repository.complete_session(session_id)
    
    def get_topic_stats(self, topic_id: int) -> Dict[str, Any]:
        """Get statistics for a topic"""
        topic = self.repository.get_topic_by_id(topic_id)
        if not topic:
            return {}
        
        # Get aggregate stats
        sessions = QuizSession.objects.filter(topic_id=topic_id, end_time__isnull=False)
        avg_score = sessions.aggregate(avg_score=Avg('score'))['avg_score'] or 0
        total_sessions = sessions.count()
        total_questions = Question.objects.filter(topic_id=topic_id).count()
        
        return {
            'topic': topic,
            'avg_score': avg_score,
            'total_sessions': total_sessions,
            'total_questions': total_questions,
        }
    
    def generate_quiz_from_document(self, document_id: int, num_questions: int = 10) -> List[Question]:
        """Generate quiz questions from a document (placeholder for RAG implementation)"""
        # This would be integrated with the RAG service in a full implementation
        # For now, we'll return an empty list
        return []
