# chat_parser.py
import re
from datetime import datetime

LINE_PATTERN = re.compile(
    r"(\d{1,2}[/.]\d{1,2}[/.]\d{2,4}),\s"  # Date (Group 1)
    r"(\d{1,2}:\d{2}(?:\s?[AP]M)?)"      # Time (Group 2)
    r"\s-\s"                             # Separator
    r"([^:]+?):\s"                       # Author (Group 3)
    r"(.+)"                              # Message (Group 4)
)

SYSTEM_MESSAGE_PATTERN = re.compile(
    r"(\d{1,2}[/.]\d{1,2}[/.]\d{2,4}),\s"  # Date (Group 1)
    r"(\d{1,2}:\d{2}(?:\s?[AP]M)?)"      # Time (Group 2)
    r"\s-\s"                             # Separator
    r"(.+)"                              # Message (Group 3) - everything after " - "
)

def parse_chat_file(filepath):
    messages = []
    current_message_dict = None # Holds the data for the message being built

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_number, line_content in enumerate(f):
            line_content = line_content.strip()
            if not line_content:
                continue

            match = LINE_PATTERN.match(line_content)
            system_match = None
            if not match:
                system_match = SYSTEM_MESSAGE_PATTERN.match(line_content)

            if match or system_match:
                if current_message_dict: # Finalize the previous message
                    messages.append(current_message_dict)

                current_message_dict = {} # Reset for the new message

                if match:
                    date_str, time_str, sender, message_text = match.groups()
                    current_message_dict['sender'] = sender.strip()
                else: # system_match must be true
                    date_str, time_str, message_text = system_match.groups()
                    current_message_dict['sender'] = "System"

                current_message_dict['message'] = message_text.strip()

                timestamp_str = f"{date_str} {time_str}"
                dt_obj = None
                formats_to_try = [
                    "%d/%m/%y %I:%M %p", "%d/%m/%Y %I:%M %p",
                    "%m/%d/%y %I:%M %p", "%m/%d/%Y %I:%M %p",
                    "%d.%m.%y %I:%M %p", "%d.%m.%Y %I:%M %p",
                    "%d/%m/%y %H:%M",    "%d/%m/%Y %H:%M",
                    "%m/%d/%y %H:%M",    "%m/%d/%Y %H:%M",
                    "%d.%m.%y %H:%M",    "%d.%m.%Y %H:%M",
                ]

                for fmt in formats_to_try:
                    try:
                        dt_obj = datetime.strptime(timestamp_str, fmt)
                        break
                    except ValueError:
                        continue

                current_message_dict['timestamp'] = dt_obj if dt_obj else timestamp_str

            elif current_message_dict: # Continuation line
                current_message_dict['message'] += "\n" + line_content # Use \n for literal

            else: # Orphan line
                messages.append({
                    'timestamp': f"Line {line_number+1}",
                    'sender': "Unknown",
                    'message': line_content
                })

    if current_message_dict: # Append the last message
        messages.append(current_message_dict)

    return messages
