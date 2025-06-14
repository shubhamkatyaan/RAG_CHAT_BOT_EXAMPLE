import re
import time
from typing import Optional
from email.utils import parseaddr

class ConversationManager:
    # In-memory session store: { user_id: { collected: {...}, started_at: timestamp, confirm_pending: bool } }
    sessions = {}

    field_order = ["name", "phone_number", "email", "complaint_details"]

    field_questions = {
        "name": "I'm sorry to hear that. Please provide your name.",
        "phone_number": "Thank you, {name}. What is your phone number?",
        "email": "Got it. Please provide your email address.",
        "complaint_details": "Thanks. Can you share more details about the issue?"
    }

    expiry_seconds = 300  # 5 minutes

    @classmethod
    def _is_valid_phone(cls, phone: str) -> bool:
        return phone.isdigit() and 7 <= len(phone) <= 15

    @classmethod
    def _is_valid_email(cls, email: str) -> bool:
        return "@" in parseaddr(email)[1]

    @classmethod
    def _reset_session(cls, user_id: str):
        if user_id in cls.sessions:
            del cls.sessions[user_id]

    @classmethod
    def _triggered(cls, text: str) -> bool:
        return bool(re.search(r"(file|raise|log|register|report|submit).*complaint", text, re.IGNORECASE)) \
            or text.lower().strip() in ["i want to file a complaint", "report a problem"]

    @classmethod
    def handle_message(cls, user_id: str, text: str):
        now = time.time()
        session = cls.sessions.get(user_id)

        if session and (now - session.get("started_at", now)) > cls.expiry_seconds:
            cls._reset_session(user_id)
            session = None

        if session is None:
            if cls._triggered(text):
                cls.sessions[user_id] = {
                    "collected": {},
                    "started_at": now,
                    "confirm_pending": False
                }
                return cls.field_questions["name"], False, {}

            return None, False, {}

        # Support field correction
        for field in cls.field_order:
            if f"change {field}" in text.lower():
                cls.sessions[user_id]["collected"].pop(field, None)
                question = cls.field_questions[field].format(name=cls.sessions[user_id]["collected"].get("name", ""))
                return f"No problem. {question}", False, {}

        collected = session["collected"]

        # Handle confirmation
        if session.get("confirm_pending"):
            if text.lower() in ["yes", "y", "submit"]:
                data = collected.copy()
                cls._reset_session(user_id)
                return None, True, data
            else:
                cls._reset_session(user_id)
                return "Okay, your complaint was not submitted. If you’d like to try again, just let me know.", False, {}

        # Ask next missing field
        for field in cls.field_order:
            if field not in collected:
                value = text.strip()

                if field == "phone_number" and not cls._is_valid_phone(value):
                    return "Please enter a valid phone number (7–15 digits).", False, {}

                if field == "email" and not cls._is_valid_email(value):
                    return "Please enter a valid email address.", False, {}

                collected[field] = value
                session["collected"] = collected

                remaining = [f for f in cls.field_order if f not in collected]
                if remaining:
                    next_q = cls.field_questions[remaining[0]].format(name=collected.get("name", ""))
                    return next_q, False, {}

                # All collected — confirm
                preview = (
                    f"Here's what I have:\n"
                    f"Name: {collected['name']}\n"
                    f"Phone: {collected['phone_number']}\n"
                    f"Email: {collected['email']}\n"
                    f"Details: {collected['complaint_details']}\n"
                    f"Shall I submit this? (yes/no)"
                )
                session["confirm_pending"] = True
                return preview, False, {}

        cls._reset_session(user_id)
        return None, True, collected
