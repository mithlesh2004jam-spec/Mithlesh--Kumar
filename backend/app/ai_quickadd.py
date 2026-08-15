def parse_task(description: str):
    text = description.lower().strip()

    # Priority
    if "urgent" in text or "high priority" in text or "important" in text:
        priority = "high"
    elif "low priority" in text or "not urgent" in text:
        priority = "low"
    else:
        priority = "medium"

    # Due date hint
    due_date_hint = None

    if "today" in text:
        due_date_hint = "today"
    elif "tomorrow" in text:
        due_date_hint = "tomorrow"
    elif "next friday" in text:
        due_date_hint = "next friday"
    elif "next week" in text:
        due_date_hint = "next week"

    # Title
    title = description.strip()

    return {
        "title": title,
        "priority": priority,
        "due_date_hint": due_date_hint,
    }