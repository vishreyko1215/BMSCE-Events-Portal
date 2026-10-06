import json
import re
import os
import sys
from datetime import datetime

def parse_events_from_chat(file_path):
    """
    Parse WhatsApp chat file and extract individual events
    """
    events = []
    threshold_date = datetime(2025, 1, 1) # Set filter to Jan 1st, 2025
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    lines = content.split('\n')
    current_event = None
    event_lines = []
    collecting = False
    
    for i, line in enumerate(lines):
        if '.jpg (file attached)' in line:
            # 1. Process and save the previous event if it exists
            if collecting and event_lines and current_event:
                event_text = '\n'.join(event_lines)
                parsed_event = parse_event_details(event_text, current_event)
                if parsed_event:
                    events.append(parsed_event)
            
            # 2. Reset for the new potential event
            collecting = False 
            event_lines = []
            
            # 3. Parse timestamp and check if it's after 01/01/2025
            try:
                parts = line.split(' - ')
                if len(parts) >= 2:
                    timestamp_str = parts[0].strip() # e.g., "11/11/25, 5:51 pm"
                    
                    # Clean the timestamp for parsing
                    # WhatsApp uses non-breaking spaces and different dash types sometimes
                    clean_ts = timestamp_str.replace('\u202f', ' ').replace('\u202f', ' ')
                    
                    # Format: Day/Month/Year, Hour:Minute AM/PM
                    # Adjusting to %y for 2-digit years (25) or %Y for 4-digit years
                    try:
                        event_date = datetime.strptime(clean_ts.split(',')[0], '%d/%m/%y')
                    except ValueError:
                        # Fallback for 4-digit years if present
                        event_date = datetime.strptime(clean_ts.split(',')[0], '%d/%m/%Y')

                    if event_date >= threshold_date:
                        collecting = True
                        sender_part = parts[1].split(':')[0].strip()
                        sender = re.sub(r'^\+\d+\s+', '', sender_part)
                        current_event = {
                            'starter_line': line,
                            'timestamp': timestamp_str,
                            'sender': sender
                        }
            except Exception as e:
                print(f"Skipping line due to date parsing error: {e}")
                continue

        elif collecting:
            event_lines.append(line)

    # Wrap up the final event in the file
    if collecting and event_lines and current_event:
        event_text = '\n'.join(event_lines)
        parsed_event = parse_event_details(event_text, current_event)
        if parsed_event:
            events.append(parsed_event)
            
    return events

def parse_event_details(event_text, starter_info):
    try:
        # Clean event text
        lines = [line.rstrip() for line in event_text.split('\n')]
        while lines and not lines[-1].strip():
            lines.pop()
        
        event_text_clean = '\n'.join(lines)
        event = {'raw_text': event_text_clean, 'extracted_details': {}}
        if isinstance(starter_info, dict):
            event.update(starter_info)
        
        all_lines = event_text_clean.split('\n')
        
        # 1. EXTRACT TITLE
        title = None
        for i, line in enumerate(all_lines):
            line_s = line.strip()
            # Added more emoji exclusions to ensure we don't pick metadata as a title
            if not line_s or any(emoji in line_s for emoji in ['📅', '⏰', '📍', '🗓️', '🕑', '🔗', '📸', '⚠️', '📜', '🤝', '📞']): continue
            if re.match(r'^Warm Rotaract', line_s, re.IGNORECASE): continue
            
            if len(line_s) > 5:
                if ':' not in line and ' - ' not in line and not line.startswith('For ') and not line.startswith('Contact'):
                    title = line_s
                    break
                    
        if title:
            clean_title = re.sub(r'[*_]', '', title)
            clean_title = re.sub(r'[^\x00-\x7F]+', '', clean_title).strip()
            event['extracted_details']['title'] = clean_title

        # 2. DATE EXTRACTION
        date_range_pattern = r'(?:📅|🗓️)\s*(?:Dates?:?\s*)?([^\n]*?(?:\d+(?:st|nd|rd|th)?\s*[-–至toand]+\s*\d+(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{0,4}|\d+(?:st|nd|rd|th)?(?:\s*[-–]\s*\d+(?:st|nd|rd|th)?)?\s+[A-Za-z]+)[^\n]*)'
        date_match = re.search(date_range_pattern, event_text_clean, re.IGNORECASE)
        if date_match:
            event['extracted_details']['date'] = re.sub(r'[*_]', '', date_match.group(1)).strip()

        # 3. DESCRIPTION EXTRACTION (FIXED: Use 'continue' instead of 'break')
        description_lines = []
        for line in all_lines:
            line_s = line.strip()
            if not line_s: continue
            if re.match(r'^Warm Rotaract', line_s, re.IGNORECASE) or line_s == title: continue
            
            # CHANGE: Instead of breaking, we skip metadata lines to keep them out of description
            # but allow the script to continue to the end of the text
            if any(marker in line_s for marker in ['📅', '⏰', '📍', '🗓️', '🕑', '🔗', '📞']): 
                continue 
            
            clean_line = re.sub(r'[*_]', '', line_s)
            description_lines.append(clean_line)

        if description_lines:
            event['extracted_details']['description'] = ' '.join(description_lines)
        elif title:
            event['extracted_details']['description'] = event['extracted_details']['title']

        # 4. LOCATION & REGISTRATION
        loc_match = re.search(r'📍\s*(?:Location|Venue|Place)[:\s]*([^\n]+)', event_text_clean, re.IGNORECASE)
        if loc_match: event['extracted_details']['location'] = re.sub(r'[*_]', '', loc_match.group(1)).strip()

        reg_match = re.search(r'(https?://forms\.gle/[^\s\n]+)', event_text_clean)
        if reg_match: event['extracted_details']['registration_link'] = reg_match.group(1).strip()

        # 5. CONTACT EXTRACTION (FIXED REGEX)
        contacts = []
        # Improved regex to handle "Rtr. Name: 1234567890" and similar formats
        contact_pattern = r'(?:📞\s*)?([A-Za-z\.\s]+)(?::|—|-)\s*(\+?\d[\d\s-]{8,15})'
        
        contact_matches = re.findall(contact_pattern, event_text_clean)
        
        for name, phone in contact_matches:
            clean_name = re.sub(r'[*_]', '', name).strip()
            # Filter out common false positives
            if clean_name.lower() not in ['contact', 'for more info', 'queries', 'date', 'time', 'location']:
                contacts.append({
                    'name': clean_name,
                    'phone': phone.strip()
                })
        
        # Fallback: Capture standalone 10-digit numbers if no name-phone pairs found
        if not contacts:
            standalone_phones = re.findall(r'\b\d{10}\b', event_text_clean)
            for phone in standalone_phones:
                contacts.append({'name': 'General Inquiry', 'phone': phone})

        event['extracted_details']['contacts'] = contacts
        
        return event

    except Exception as e:
        print(f"Error parsing event details: {e}")
        return {**starter_info, 'raw_text': event_text, 'parse_error': str(e)}

def save_events_to_single_json(events, input_filename):
    """
    Saves events to a JSON file. 
    Matches the naming convention used in the HTML router.
    """
    try:
        # Determine output name based on input to avoid overwriting different clubs
        # If input is 'FLEETS 2024-25.txt', output becomes 'fleet_events_collections_all.json'
        if 'FLEET' in input_filename.upper():
            output_file = 'fleet_events_collections_all.json'
        elif 'ROTARACT' in input_filename.upper() :
            output_file = 'rotaract_events_collections_all.json'
        else:
            output_file = 'events_collections_all.json'

        events_collection = {
            "metadata": {
                "total_events": len(events),
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source_file": input_filename
            },
            "events": events
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(events_collection, f, indent=2, ensure_ascii=False)
        
        return output_file
    except Exception as e:
        print(f"Error saving: {e}")
        return None

def main():
    # Check for command line argument
    if len(sys.argv) < 2:
        print("Error: No input file specified.")
        print("Usage: python parse_events_single_json.py <filename.txt>")
        return

    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return
    
    print(f"--- Starting Parse: {input_file} ---")
    events = parse_events_from_chat(input_file)
    
    output_path = save_events_to_single_json(events, input_file)
    
    if output_path:
        print(f"Successfully created {output_path} with {len(events)} events.")

if __name__ == "__main__":
    main()