# -*- coding: utf-8 -*-
"""
AI Chatbot Module using Google Generative AI (Gemini)
Handles technical problem solving, HR queries, and project management guidance
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except (ImportError, Exception) as e:



    
    GENAI_AVAILABLE = False
    print(f"[WARN] Google Generative AI not available: {e}")

from database import get_db, close_db
import uuid
from datetime import datetime


class AIAssistant:
    def __init__(self, api_key=None):
        """Initialize the AI Assistant with Google Generative AI"""
        if not GENAI_AVAILABLE:
            raise ValueError(
                "Google Generative AI is not available. "
                "Install it with: pip install google-generativeai"
            )
        
        if not api_key:
            api_key = os.getenv('GOOGLE_API_KEY')
        
        if not api_key:
            raise ValueError(
                "Google API Key not found. Set GOOGLE_API_KEY environment variable "
                "or pass it as a parameter. Get it from: https://makersuite.google.com/app/apikey"
            )
        
        genai.configure(api_key=api_key)
        
        # Try modern models first, fallback to classic gemini-pro
        model_names = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
        
        self.model = None
        for model_name in model_names:
            try:
                # Just create the model object without testing (tests happen on first use)
                self.model = genai.GenerativeModel(model_name)
                print(f"[OK] Initialized Gemini model: {model_name}")
                break
            except Exception as e:
                print(f"[WARN] Model {model_name} initialization failed: {str(e)[:60]}")
                continue
        
        if not self.model:
            # If nothing worked, try to use the first available model from list
            try:
                models = genai.list_models()
                for m in models:
                    if 'generateContent' in m.supported_generation_methods:
                        self.model = genai.GenerativeModel(m.name)
                        print(f"[OK] Using first available model: {m.name}")
                        break
            except Exception as e:
                print(f"[WARN] Could not list models: {e}")
        
        if not self.model:
            raise ValueError("Could not initialize any Gemini model. Please check your API key.")
        
        self.api_key_set = True
    
    def get_system_prompt(self, user_type='employee'):
        """Get the system prompt based on user type"""
        base_prompt = """You are an intelligent workplace assistant helping employees and administrators with:
1. **Technical Issues**: Troubleshooting software, hardware, network, and system problems
2. **HR & Leave Policies**: Explaining leave policies, benefits, payroll, performance reviews
3. **Project Management**: Guidance on project planning, task management, deadlines, and team coordination
4. **General Workplace Questions**: Schedules, policies, procedures, best practices

Be professional, helpful, and concise. Provide actionable solutions.
If you don't know something, admit it and suggest asking the HR/IT team."""

        if user_type == 'admin':
            base_prompt += "\n\nAs an ADMIN user, you have access to manage employee policies, resolve system issues, and provide administrative guidance."
        else:
            base_prompt += "\n\nYou are assisting an EMPLOYEE. Provide guidance within the scope of their role."
        
        return base_prompt
    
    def categorize_message(self, message):
        """Categorize the user message into a topic"""
        message_lower = message.lower()
        
        technical_keywords = ['error', 'bug', 'crash', 'not working', 'broken', 'issue', 'problem', 'fix',
                            'restart', 'password', 'login', 'system', 'network', 'wifi', 'internet', 'slow']
        hr_keywords = ['leave', 'salary', 'payroll', 'benefits', 'policy', 'holiday', 'vacation', 'bonus',
                       'appraisal', 'review', 'promotion', 'performance', 'attendance']
        project_keywords = ['project', 'task', 'deadline', 'milestone', 'progress', 'sprint', 'update',
                           'assignment', 'deliverable', 'timeline', 'budget']
        
        if any(keyword in message_lower for keyword in technical_keywords):
            return 'technical'
        elif any(keyword in message_lower for keyword in hr_keywords):
            return 'hr_policy'
        elif any(keyword in message_lower for keyword in project_keywords):
            return 'project_management'
        else:
            return 'general'
    
    def get_response(self, user_message, user_type='employee', conversation_context=None):
        """Get AI response to user message"""
        try:
            system_prompt = self.get_system_prompt(user_type)
            category = self.categorize_message(user_message)
            
            # Build context-aware prompt
            context_info = ""
            if conversation_context:
                context_info = f"\n\nPrevious conversation context:\n{conversation_context}\n"
            
            full_prompt = f"{system_prompt}\n\n[Message Category: {category}]{context_info}\n\nUser Question: {user_message}"
            
            # Get response from Gemini
            response = self.model.generate_content(full_prompt)
            
            if response and response.text:
                return {
                    'success': True,
                    'response': response.text,
                    'category': category
                }
            else:
                return {
                    'success': False,
                    'response': 'Unable to generate response. Please try again.',
                    'category': category
                }
        
        except Exception as e:
            return {
                'success': False,
                'response': f'Error: {str(e)}',
                'category': 'error'
            }
    
    def save_conversation_message(self, user_id, user_type, user_message, bot_response, category='general'):
        """Save conversation to database"""
        try:
            conn = get_db()
            
            # Get or create conversation
            today = datetime.now().date().isoformat()
            conversation = conn.execute(
                "SELECT conversation_id FROM chatbot_conversations WHERE user_id=? AND user_type=? AND DATE(created_at)=?",
                (user_id, user_type, today)
            ).fetchone()
            
            if not conversation:
                conversation_id = str(uuid.uuid4())
                conn.execute("""
                    INSERT INTO chatbot_conversations (user_id, user_type, conversation_id, topic)
                    VALUES (?, ?, ?, ?)
                """, (user_id, user_type, conversation_id, category))
            else:
                conversation_id = conversation['conversation_id']
            
            # Save the message exchange
            conn.execute("""
                INSERT INTO chatbot_messages (conversation_id, user_id, user_message, bot_response, message_category)
                VALUES (?, ?, ?, ?, ?)
            """, (conversation_id, user_id, user_message, bot_response, category))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False
        finally:
            close_db(conn)
    
    def get_conversation_history(self, user_id, user_type, limit=5):
        """Retrieve recent conversation history for context"""
        try:
            conn = get_db()
            
            messages = conn.execute("""
                SELECT user_message, bot_response, created_at
                FROM chatbot_messages
                WHERE conversation_id IN (
                    SELECT conversation_id FROM chatbot_conversations 
                    WHERE user_id=? AND user_type=?
                )
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, user_type, limit)).fetchall()
            
            context = ""
            for msg in reversed(messages):
                context += f"User: {msg['user_message'][:100]}...\nAssistant: {msg['bot_response'][:100]}...\n\n"
            
            return context
        except Exception as e:
            print(f"Error retrieving conversation: {e}")
            return ""
        finally:
            close_db(conn)
    
    def get_user_conversations(self, user_id, user_type, limit=10):
        """Get list of recent conversations for a user"""
        try:
            conn = get_db()
            
            conversations = conn.execute("""
                SELECT conversation_id, topic, created_at, updated_at,
                       (SELECT COUNT(*) FROM chatbot_messages WHERE conversation_id=chatbot_conversations.conversation_id) as message_count
                FROM chatbot_conversations
                WHERE user_id=? AND user_type=?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (user_id, user_type, limit)).fetchall()
            
            return conversations
        except Exception as e:
            print(f"Error retrieving conversations: {e}")
            return []
        finally:
            close_db(conn)


def get_ai_assistant(api_key=None):
    """Factory function to get AI Assistant instance"""
    try:
        return AIAssistant(api_key)
    except ValueError as e:
        print(f"Warning: {e}")
        return None
