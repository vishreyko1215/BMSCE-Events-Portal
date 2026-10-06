# BMSCE Events Portal

A centralized web portal for discovering BMSCE college events and club activities.

## Overview

The BMSCE Events Portal was developed to make college events easier to discover by bringing event information from different club announcements and WhatsApp messages into one centralized platform.

The project combines a web-based frontend with Python-based event data processing and structured JSON data.

## Problem

College event information is often scattered across WhatsApp groups and individual club announcements. This makes it difficult for students to discover upcoming events and find information about different clubs.

The portal addresses this problem by organizing event information into a centralized and accessible platform.

## Features

- 🏠 Centralized event dashboard
- 🎓 Club discovery
- 📅 Upcoming event listings
- 🔎 Event search and navigation
- 📋 Detailed event information
- 🏷️ Event categories
- 🔄 Dynamic event display using JSON data
- 🐍 Python-based event data processing

## How It Works

1. Event information is collected from club announcements and WhatsApp chat data.
2. The Python parser extracts relevant event information such as:
   - Event name
   - Date
   - Time
   - Venue
   - Club
3. The processed information is stored as structured JSON data.
4. The frontend reads the JSON data.
5. Events and club information are dynamically displayed through the web interface.

## Technology Stack

- **HTML**
- **CSS**
- **JavaScript**
- **Python**
- **JSON**

## Project Structure

```text
BMSCE-Events-Portal/
├── index.html
├── parse_events_single_json.py
├── run_parser.bat
├── *.json
├── *.txt
├── bms.png
└── README.md

My Contribution
My primary contribution to this project was the frontend and UI implementation.
I worked on:
- Designing the web interface
- Implementing the frontend using HTML and CSS
- Creating interactive elements using JavaScript
- Designing the event and club discovery experience
- Implementing event detail views
- Organizing the interface for easier navigation

Future Improvements
- Admin login and event management
- Database integration
- Event notifications
- Advanced search and filtering
- Improved event management workflows

Screenshots:
The project screenshots and interface designs can be found in the project documentation and portfolio case study.