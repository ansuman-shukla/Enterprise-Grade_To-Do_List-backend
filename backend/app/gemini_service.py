import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
import google.generativeai as genai
from dateutil import parser
from .models import GeminiResponse, Priority
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        logger.info(f"DEBUG: API Key loaded: {self.api_key is not None}")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set - Gemini service will not be available")
            self.model = None
            self.is_configured = False
            return
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name='gemini-2.0-flash'
            )
            self.is_configured = True
            logger.info("Gemini service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            self.model = None
            self.is_configured = False  

    def _get_current_date_context(self) -> str:
        """Get current date context for relative date parsing"""
        now = datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')} at {now.strftime('%I:%M %p')}"

    def _create_prompt(self, user_input: str) -> str:
        """Create the prompt for Gemini"""
        current_date = self._get_current_date_context()

        prompt = f"""You are a helpful assistant that parses task descriptions into structured data.

        {current_date}

        Extract the following information from the user's task input:

        1. **Task Name**: The core action or item to be done (required)
        2. **Assignee**: The person assigned to the task. Look for names, "me", "I", or phrases like "assigned to X". If no specific person is mentioned, return null.
        3. **Due Date and Time**: Parse any date/time mentions including:
        - Specific dates: "June 20th", "2024-06-20"
        - Relative dates: "tomorrow", "next Tuesday", "next week"
        - Times: "3pm", "15:00", "at 3:30"
        - If mentioned, format as YYYY-MM-DDTHH:MM:SS
        - If no due date/time is mentioned, return null
        4. **Priority**: Look for P1, P2, P3, or P4 mentions. If found, extract that. Otherwise, return null.

        Return ONLY a valid JSON object with these exact keys: "task_name", "assignee", "due_date_time", "priority_hint"

        Examples:
        Input: "Schedule meeting with Marketing team for next Tuesday at 3pm P1"
        Output: {{"task_name": "Schedule meeting with Marketing team", "assignee": null, "due_date_time": "2024-06-04T15:00:00", "priority_hint": "P1"}}

        Input: "Buy groceries tomorrow assigned to John"
        Output: {{"task_name": "Buy groceries", "assignee": "John", "due_date_time": "2024-05-30T09:00:00", "priority_hint": null}}

        User input: "{user_input}"

        JSON Output:"""

        return prompt

    async def parse_task(self, user_input: str) -> Optional[GeminiResponse]:
        """Parse natural language task input using Gemini"""
        if not self.is_configured:
            logger.error("Gemini service is not configured - cannot parse task")
            return None

        try:
            prompt = self._create_prompt(user_input)

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Clean up the response to extract JSON
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            # Parse JSON response
            parsed_data = json.loads(response_text)

            # Validate and create GeminiResponse
            gemini_response = GeminiResponse(**parsed_data)

            logger.info(f"Successfully parsed task: {gemini_response}")
            return gemini_response

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {e}")
            logger.error(f"Raw response: {response_text}")
            return None
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return None

    def parse_datetime(self, date_string: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object"""
        if not date_string:
            return None

        try:
            # Try to parse the datetime string
            parsed_date = parser.parse(date_string)
            return parsed_date
        except Exception as e:
            logger.error(f"Failed to parse datetime '{date_string}': {e}")
            return None

    def parse_priority(self, priority_hint: Optional[str]) -> Priority:
        """Parse priority hint to Priority enum"""
        if not priority_hint:
            return Priority.P3

        priority_upper = priority_hint.upper()
        if priority_upper in ["P1", "P2", "P3", "P4"]:
            return Priority(priority_upper)

        return Priority.P3


# Global instance
gemini_service = GeminiService()
