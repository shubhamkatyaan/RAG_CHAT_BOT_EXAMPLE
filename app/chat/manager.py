import re

class ConversationManager:
    # In-memory session store: { user_id: { collected: {field: value} } }
    sessions = {}
    field_order = ["name", "phone_number", "email", "complaint_details"]
    field_questions = {
        "name": "I'm sorry to hear that. Please provide your name.",
        "phone_number": "Thank you, {name}. What is your phone number?",
        "email": "Got it. Please provide your email address.",
        "complaint_details": "Thanks. Can you share more details about the issue?"
    }

    @classmethod
    def handle_message(cls, user_id: str, text: str):
        # Start or resume a complaint session
        session = cls.sessions.get(user_id)

        # If no session and user wants to file a complaint
        if session is None:
            if re.search(r"\b(file|raise|log)\b.*\bcomplaint\b", text, re.IGNORECASE):
                cls.sessions[user_id] = {"collected": {}}
                # Ask for the first field
                return cls.field_questions["name"].format(name=""), False, {}
            # Not a complaint-related message
            return None, False, {}

        # Resume existing session
        collected = session["collected"]
        # Determine the next missing field
        for field in cls.field_order:
            if field not in collected:
                # Save the user response for this field
                collected[field] = text.strip()
                session["collected"] = collected
                # If more fields remain, ask next question
                remaining = [f for f in cls.field_order if f not in collected]
                if remaining:
                    next_q = cls.field_questions[remaining[0]].format(name=collected.get("name", ""))
                    return next_q, False, {}
                # All fields collected
                data = collected.copy()
                # Clean up session
                del cls.sessions[user_id]
                return None, True, data

        # Fallback: treat as done
        del cls.sessions[user_id]
        return None, True, collected
