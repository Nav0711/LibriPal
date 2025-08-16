import google.generativeai as genai
import os
import json
import asyncio
from typing import List, Dict, Optional
from models.pydantic_models import Book, AIAnalysis, BookRecommendation

class AIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_book_summary(self, title: str, author: str, description: str = "") -> str:
        """Generate AI summary for a book"""
        try:
            prompt = f"""
            Generate a concise, helpful summary for this book that would help students understand what it covers:
            
            Title: {title}
            Author: {author}
            Description: {description}
            
            Provide a 2-3 sentence summary that highlights:
            - Key topics and concepts covered
            - Target audience (students, professionals, beginners, advanced)
            - What makes this book valuable for learning
            
            Keep it informative and engaging for students.
            """
            
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"Error generating AI summary: {e}")
            return f"A comprehensive book by {author} covering topics related to {title}."
    
    async def analyze_chat_message(self, message: str, user_context: Dict) -> Dict:
        """Analyze chat message to determine intent and extract information"""
        try:
            prompt = f"""
            You are LibriPal, an AI library assistant. Analyze this user message and determine the intent:
            
            User message: "{message}"
            User context: Has borrowed {user_context.get('borrowed_count', 0)} books currently
            
            Possible intents:
            - book_search: user wants to find/search for books
            - reservation: user wants to reserve/borrow a specific book
            - renewal: user wants to renew borrowed books
            - due_dates: user wants to check due dates or overdue status
            - recommendations: user wants book recommendations
            - fines: user wants to check fines/fees
            - library_info: user wants library information (hours, rules, policies)
            - help: general help or unclear intent
            
            Extract relevant information and respond with JSON:
            {{
                "intent": "detected_intent",
                "confidence": 0.9,
                "extracted_info": {{
                    "search_query": "extracted search terms if any",
                    "book_title": "specific book title if mentioned",
                    "topic": "subject area if mentioned"
                }},
                "response_suggestion": "Friendly, helpful response to the user"
            }}
            
            Be conversational and helpful in your response suggestion.
            """
            
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            try:
                # Clean the response text and parse JSON
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3]
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3]
                
                ai_response = json.loads(response_text)
                return ai_response
                
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "intent": "help",
                    "confidence": 0.5,
                    "extracted_info": {},
                    "response_suggestion": "I'd be happy to help you with your library needs! You can ask me to search for books, check due dates, renew books, or get recommendations."
                }
        
        except Exception as e:
            print(f"Error analyzing chat message: {e}")
            return {
                "intent": "help",
                "confidence": 0.5,
                "extracted_info": {},
                "response_suggestion": "I'd be happy to help you with your library needs!"
            }
    
    async def get_personalized_recommendations(self, user_id: int, query: str = "") -> List[Book]:
        """Get AI-powered book recommendations"""
        try:
            # This would typically fetch user's reading history from database
            # For now, we'll use a simplified approach
            
            prompt = f"""
            Based on the user's request: "{query}"
            
            Suggest 5 academic/educational books that would be valuable for a student.
            Focus on popular, well-regarded books in computer science, engineering, mathematics, or related fields.
            
            Format each recommendation as:
            Title: [Book Title]
            Author: [Author Name]
            Reason: [Why this book is recommended]
            
            Make sure these are real, well-known books that would typically be found in a university library.
            """
            
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            # Parse the response (this is simplified - in production you'd search actual database)
            recommendations = []
            lines = response.text.split('\n')
            current_book = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('Title:'):
                    if current_book:
                        recommendations.append(current_book)
                    current_book = {'title': line[6:].strip()}
                elif line.startswith('Author:'):
                    current_book['author'] = line[7:].strip()
                elif line.startswith('Reason:'):
                    current_book['reason'] = line[7:].strip()
            
            if current_book:
                recommendations.append(current_book)
            
            # Convert to Book objects (simplified)
            book_recommendations = []
            for i, rec in enumerate(recommendations[:5]):
                book = Book(
                    id=i + 1000,  # Fake IDs for demo
                    title=rec.get('title', 'Unknown Title'),
                    author=rec.get('author', 'Unknown Author'),
                    description=rec.get('reason', ''),
                    total_copies=1,
                    available_copies=1,
                    ai_summary=rec.get('reason', ''),
                    created_at="2025-08-16T10:17:42Z"
                )
                book_recommendations.append(book)
            
            return book_recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []
    
    async def generate_reading_insights(self, user_reading_data: List[Dict]) -> Dict:
        """Generate AI insights about user's reading patterns"""
        try:
            books_summary = "\n".join([
                f"- {book['title']} by {book['author']} ({book['genre']})"
                for book in user_reading_data[-10:]  # Last 10 books
            ])
            
            prompt = f"""
            Analyze this user's reading history and provide insights:
            
            Recent books:
            {books_summary}
            
            Provide a JSON response with:
            {{
                "reading_patterns": "Description of reading preferences and patterns",
                "suggested_genres": ["list", "of", "suggested", "genres"],
                "growth_areas": "Areas where the user could expand their reading",
                "achievements": "Positive observations about their reading journey"
            }}
            
            Be encouraging and insightful.
            """
            
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            try:
                return json.loads(response.text.strip())
            except json.JSONDecodeError:
                return {
                    "reading_patterns": "You have diverse reading interests!",
                    "suggested_genres": ["Computer Science", "Mathematics"],
                    "growth_areas": "Consider exploring new domains",
                    "achievements": "Great job maintaining consistent reading habits!"
                }
                
        except Exception as e:
            print(f"Error generating reading insights: {e}")
            return {}
    
    async def enhance_search_query(self, query: str) -> str:
        """Enhance user search query for better results"""
        try:
            prompt = f"""
            Enhance this library search query to find more relevant academic books:
            
            Original query: "{query}"
            
            Provide an enhanced search query that:
            - Includes relevant synonyms and related terms
            - Focuses on academic/educational content
            - Uses proper terminology
            
            Return only the enhanced query, nothing else.
            """
            
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            enhanced_query = response.text.strip().strip('"')
            
            return enhanced_query if enhanced_query != query else query
            
        except Exception as e:
            print(f"Error enhancing search query: {e}")
            return query
    
    async def generate_study_suggestions(self, book_title: str, user_level: str = "intermediate") -> List[str]:
        """Generate study suggestions for a specific book"""
        try:
            prompt = f"""
            Provide 5 study tips for someone reading "{book_title}" at {user_level} level:
            
            Format as a simple list of actionable suggestions.
            Focus on effective learning strategies.
            """
            
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            # Parse suggestions
            suggestions = []
            for line in response.text.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                    # Clean up formatting
                    suggestion = line.lstrip('-•0123456789. ').strip()
                    if suggestion:
                        suggestions.append(suggestion)
            
            return suggestions[:5]
            
        except Exception as e:
            print(f"Error generating study suggestions: {e}")
            return [
                "Take notes while reading key concepts",
                "Practice examples and exercises",
                "Discuss concepts with peers",
                "Review previous chapters regularly",
                "Apply concepts to real projects"
            ]