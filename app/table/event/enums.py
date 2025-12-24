from enum import Enum


class EventType(str, Enum):
    """Known event types."""

    # Rate Us events
    RATE_SHEET_SHOWN = "rate_sheet_shown"
    RATE_SLIDER_COMPLETED = "rate_slider_completed"
    RATE_SHEET_CLOSED = "rate_sheet_closed"

    # Push events
    PUSH_PROMPT_SHOWN = "push_prompt_shown"
    PUSH_PROMPT_ACCEPTED = "push_prompt_accepted"
    PUSH_PROMPT_DECLINED = "push_prompt_declined"
