Robots.txt Analyzer
A web-based tool for analyzing robots.txt files across multiple websites to check for Google crawler disallow rules.

Features
Analyze robots.txt files from multiple websites simultaneously
Check if Google crawler is allowed or disallowed
View detailed disallow rules for Google user agents
Filter results by allowed, disallowed, or error status
Sort results by different columns
Export results in CSV, JSON, or plain text formats
Process up to 100+ domains in a single batch
Technical Details
Dependencies
Python 3.11
Flask (Web framework)
Requests (HTTP library)
Gunicorn (WSGI HTTP Server)
Bootstrap (Front-end framework)
Font Awesome (Icons)
Components
app.py: Main Flask application with routes and export functionality
main.py: Entry point that starts the web server
robot_analyzer.py: Core functionality for analyzing robots.txt files
templates/: HTML templates using Jinja2
layout.html: Base template with common structure
index.html: Main page with form and results table
static/: Static assets
css/custom.css: Custom styling
js/script.js: Frontend interactivity and sorting
How It Works
Users enter multiple URLs (one per line) in the form
The application fetches and analyzes the robots.txt file for each URL
Results are displayed in a sortable and filterable table
Users can export results in their preferred format
Technical Implementation
The application uses concurrent processing to analyze multiple robots.txt files simultaneously, with a configurable number of concurrent workers (default: 25). For each URL:

The URL is normalized and its robots.txt is retrieved
The robots.txt content is parsed using Python's urllib.robotparser
Rules specific to Google user agents are analyzed
Results are compiled and presented in the web interface
Getting Started
Prerequisites
Python 3.11 or higher
pip (Python package installer)
Installation
Clone this repository
Install dependencies:
pip install flask requests gunicorn
Running the Application
Start the server:
gunicorn --bind 0.0.0.0:5000 main:app
Open a web browser and navigate to http://localhost:5000
Usage
Enter URLs (one per line) in the text area
Click "Analyze Robots.txt Files" button
View the results in the table
Use the filter buttons to show specific results
Click on column headers to sort results
Use the export dropdown to download results in CSV, JSON, or text format
File Structure
├── app.py                 # Flask application
├── main.py                # Application entry point
├── robot_analyzer.py      # Core analysis functionality
├── static/
│   ├── css/
│   │   └── custom.css     # Custom styling
│   └── js/
│       └── script.js      # Frontend JavaScript
├── templates/
│   ├── index.html         # Main page template
│   └── layout.html        # Base template
├── models.py              # Unused database models
└── README.md              # This documentation
License
This project is available for personal and commercial use.

Contributing
Feel free to fork this project and submit pull requests with improvements or bug fixe
