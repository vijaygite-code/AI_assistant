import time
from datetime import datetime, timedelta
import re
import threading
import pyttsx3
import calendar

# Initialize the TTS engine
tts_engine = pyttsx3.init()

# Store reminders in lists
reminders = []
recurring_reminders = []

# Function to speak text
def speak(text):
    print(text)  # Also print the text for debugging
    tts_engine.say(text)
    tts_engine.runAndWait()

# Function to drop a message and speak it
def drop_message(message):
    print("\n" + "=" * 40)
    print(f"REMINDER: {message}")
    print("=" * 40 + "\n")
    speak(f"Reminder: {message}")

# Function to parse natural language input for reminders
def parse_reminder_input(input_text):
    recurring_patterns = {
        'day': r'(every\s*day|daily)',
        'week': r'every\s*week',
        'month': r'every\s*month',
        'year': r'every\s*year'
    }
    
    reminder_text = input_text
    recurring_type = None
    time_str = None
    date_str = None
    
    # Check for recurring patterns
    for recurrence, pattern in recurring_patterns.items():
        if re.search(pattern, input_text, re.IGNORECASE):
            recurring_type = recurrence
            # Remove the recurring pattern from the reminder text
            reminder_text = re.sub(pattern, '', input_text, flags=re.IGNORECASE).strip()
            break
    
    # Check for date in the input
    date_patterns = [
        r'(today|tomorrow|the next day)',
        r'(on|for) (\d{1,2}(?:st|nd|rd|th)? (?:of )?(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?))',
        r'(\d{1,2}(?:st|nd|rd|th)? (?:of )?(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?))'
    ]
    
    for pattern in date_patterns:
        date_match = re.search(pattern, reminder_text, re.IGNORECASE)
        if date_match:
            date_str = date_match.group()
            reminder_text = re.sub(re.escape(date_str), '', reminder_text, flags=re.IGNORECASE).strip()
            break
    
    # Check for time in the input
    time_patterns = [
        r'at (\d{1,2}(?::\d{2})?\s*(?:am|pm))',
        r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))',
        r'(\d{1,2}\s*o\'clock)',
        r'at (\w+)',  # For phrases like "at noon", "at midnight"
        r'in (\d+) (minute|minutes|hour|hours|day|days)',
    ]
    
    for pattern in time_patterns:
        time_match = re.search(pattern, reminder_text, re.IGNORECASE)
        if time_match:
            time_str = time_match.group()
            reminder_text = re.sub(re.escape(time_str), '', reminder_text, flags=re.IGNORECASE).strip()
            break
    
    return reminder_text, recurring_type, time_str, date_str

# Function to parse natural language date expressions
def parse_date_expression(date_input):
    if not date_input:
        return datetime.now().date()
    
    today = datetime.now().date()
    
    if 'today' in date_input.lower():
        return today
    elif 'tomorrow' in date_input.lower():
        return today + timedelta(days=1)
    elif 'the next day' in date_input.lower():
        return today + timedelta(days=2)
    
    # Handle specific dates like "15th August"
    date_match = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?(\w+)', date_input, re.IGNORECASE)
    if date_match:
        day = int(date_match.group(1))
        month = date_match.group(2).lower()
        month_num = list(calendar.month_abbr).index(month[:3].title())
        year = today.year
        
        # If the date has already passed this year, assume it's for next year
        parsed_date = datetime(year, month_num, day).date()
        if parsed_date < today:
            parsed_date = datetime(year + 1, month_num, day).date()
        
        return parsed_date
    
    return None

# Function to parse natural language time expressions
def parse_time_expression(time_input):
    now = datetime.now()
    
    if not time_input:
        return now.replace(hour=9, minute=0, second=0, microsecond=0)  # Default to 9:00 AM if no time specified
    
    # Handling "in X minutes/hours/days"
    relative_time_match = re.match(r'in (\d+) (minute|minutes|hour|hours|day|days)', time_input, re.IGNORECASE)
    if relative_time_match:
        value = int(relative_time_match.group(1))
        unit = relative_time_match.group(2).lower()
        
        if 'minute' in unit:
            return now + timedelta(minutes=value)
        elif 'hour' in unit:
            return now + timedelta(hours=value)
        elif 'day' in unit:
            return now + timedelta(days=value)
    
    # Handling specific times
    time_patterns = [
        (r'(?:at\s)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', lambda h, m, p: (int(h) % 12 + (12 if p and p.lower() == 'pm' else 0), int(m) if m else 0)),
        (r'(\d{1,2})\s*o\'clock', lambda h, _: (int(h) % 12, 0)),
        (r'noon', lambda: (12, 0)),
        (r'midnight', lambda: (0, 0)),
        (r'morning', lambda: (9, 0)),
        (r'afternoon', lambda: (14, 0)),
        (r'evening', lambda: (18, 0)),
        (r'night', lambda: (20, 0))
    ]
    
    for pattern, time_func in time_patterns:
        match = re.match(pattern, time_input, re.IGNORECASE)
        if match:
            if callable(time_func):
                hour, minute = time_func(*match.groups())
            else:
                hour, minute = time_func()
            
            reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            return reminder_time
    
    return None

# Function to set a reminder
def set_reminder(input_text=None):
    if not input_text:
        speak("What do you want to be reminded about?")
        input_text = input("Reminder: ")
    
    reminder_text, recurring_type, time_str, date_str = parse_reminder_input(input_text)
    
    reminder_date = parse_date_expression(date_str)
    reminder_time = parse_time_expression(time_str)
    
    if reminder_date and reminder_time:
        reminder_datetime = datetime.combine(reminder_date, reminder_time.time())
        
        if recurring_type:
            recurring_reminders.append((reminder_text, reminder_datetime.time(), recurring_type))
            speak(f"Recurring reminder set for {reminder_datetime.strftime('%I:%M %p')} on {reminder_datetime.strftime('%B %d, %Y')} {recurring_type}")
        else:
            reminders.append((reminder_text, reminder_datetime))
            speak(f"Reminder set for {reminder_datetime.strftime('%I:%M %p')} on {reminder_datetime.strftime('%B %d, %Y')}")
    else:
        speak("I couldn't understand the time or date. The reminder has been set for 9:00 AM today by default.")
        default_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        if recurring_type:
            recurring_reminders.append((reminder_text, default_time.time(), recurring_type))
        else:
            reminders.append((reminder_text, default_time))

# Function to check reminders
def check_reminders():
    while True:
        current_time = datetime.now()
        
        # Check one-time reminders
        for reminder in reminders[:]:
            reminder_text, reminder_time = reminder
            if current_time >= reminder_time:
                drop_message(reminder_text)
                reminders.remove(reminder)
        
        # Check recurring reminders
        for reminder in recurring_reminders:
            reminder_text, reminder_time, recurring_type = reminder
            if current_time.time().replace(second=0, microsecond=0) == reminder_time.replace(second=0, microsecond=0):
                drop_message(reminder_text)
                
                # Schedule the next occurrence
                if recurring_type == 'day':
                    next_reminder = current_time.replace(hour=reminder_time.hour, minute=reminder_time.minute, second=0, microsecond=0) + timedelta(days=1)
                elif recurring_type == 'week':
                    next_reminder = current_time.replace(hour=reminder_time.hour, minute=reminder_time.minute, second=0, microsecond=0) + timedelta(weeks=1)
                elif recurring_type == 'month':
                    next_reminder = current_time.replace(hour=reminder_time.hour, minute=reminder_time.minute, second=0, microsecond=0) + timedelta(days=30)  # Approximate
                elif recurring_type == 'year':
                    next_reminder = current_time.replace(hour=reminder_time.hour, minute=reminder_time.minute, second=0, microsecond=0) + timedelta(days=365)  # Approximate
                
                reminders.append((reminder_text, next_reminder))
        
        time.sleep(1)  # Check every second

# Main loop
def main():
    speak("Hello! How can I assist you today?")
    
    # Start the reminder checking thread
    reminder_thread = threading.Thread(target=check_reminders, daemon=True)
    reminder_thread.start()
    
    while True:
        print("\nType your reminder or 'exit' to quit.")
        command = input("Command: ")
        
        if command.lower() == "exit" or command.lower() == "stop":
            speak("Goodbye!")
            break
        else:
            set_reminder(command)

if __name__ == "__main__":
    main()