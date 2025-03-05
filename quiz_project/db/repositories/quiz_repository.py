from typing import List, Dict, Any, Optional
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q

from quiz.models import Topic, Question, Answer, QuizSession, QuizResponse

class QuizRepository:
    @staticmethod
    def get_topics() -> List[Topic]:
        """Get all quiz topics"""
        return list(Topic.objects.all())
    
    @staticmethod
    def get_topic_by_id(topic_id: int) -> Optional[Topic]:
        """Get a topic by ID"""
        try:
            return Topic.objects.get(id=topic_id)
        except Topic.DoesNotExist:
            return None
    
    @staticmethod
    def get_questions_for_topic(topic_id: int, limit: Optional[int] = None) -> List[Question]:
        """Get questions for a topic, optionally limited"""
        query = Question.objects.filter(topic_id=topic_id).order_by('?')
        if limit:
            query = query[:limit]
        return list(query)
    
    @staticmethod
    def start_quiz_session(user_id: int, topic_id: int, num_questions: int = 10) -> QuizSession:
        """Start a new quiz session"""
        user = User.objects.get(id=user_id)
        topic = Topic.objects.get(id=topic_id)
        
        session = QuizSession.objects.create(
            user=user,
            topic=topic,
            start_time=timezone.now()
        )
        
        # Get random questions for this topic
        questions = Question.objects.filter(topic_id=topic_id).order_by('?')[:num_questions]
        
        # Create response placeholders
        for question in questions:
            QuizResponse.objects.create(
                session=session,
                question=question
            )
        
        return session
    
    @staticmethod
    def get_session_by_id(session_id: int) -> Optional[QuizSession]:
        """Get quiz session by ID"""
        try:
            return QuizSession.objects.get(id=session_id)
        except QuizSession.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_sessions(user_id: int, topic_id: Optional[int] = None) -> List[QuizSession]:
        """Get quiz sessions for a user"""
        query = {'user_id': user_id}
        if topic_id:
            query['topic_id'] = topic_id
        return list(QuizSession.objects.filter(**query).order_by('-start_time'))
    
    @staticmethod
    def record_response(session_id: int, question_id: int, answer_id: Optional[int] = None) -> QuizResponse:
        """Record a user's response to a question"""
        # Get the response object
        response = QuizResponse.objects.get(
            session_id=session_id,
            question_id=question_id
        )
        
        # If answer_id is provided, set the selected answer
        if answer_id:
            answer = Answer.objects.get(id=answer_id)
            response.selected_answer = answer
            response.is_correct = answer.is_correct
            response.save()
        
        return response
    
    @staticmethod
    def complete_session(session_id: int) -> QuizSession:
        """Mark a quiz session as completed and calculate score"""
        session = QuizSession.objects.get(id=session_id)
        session.end_time = timezone.now()
        session.score = session.calculate_score()
        session.save()
        return session
