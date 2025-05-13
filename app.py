import os
import logging
import json
import csv
from io import StringIO
from datetime import datetime
from flask import Flask, render_template, request, jsonify, flash, Response, session
from robot_analyzer import analyze_robots_txt_urls

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

@app.route('/', methods=['GET', 'POST'])
def index():
    """Render the main page"""
    if request.method == 'POST':
        # If someone posts to the root route, redirect to analyze
        return analyze()
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Process the list of URLs and analyze their robots.txt files"""
    # Get URLs from the form
    urls_text = request.form.get('urls', '')
    
    # Split the text into a list of URLs, strip whitespace and filter out empty lines
    urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
    
    if not urls:
        flash('Please enter at least one URL', 'warning')
        return render_template('index.html')
    
    if len(urls) > 200:
        flash(f'For performance reasons, only the first 200 URLs will be analyzed. You entered {len(urls)}.', 'warning')
        urls = urls[:200]
    
    # Log the batch size for monitoring
    logging.info(f"Analyzing batch of {len(urls)} URLs")
    
    # Analyze the robots.txt files
    results = analyze_robots_txt_urls(urls)
    
    # Log completion
    logging.info(f"Completed analysis of {len(results)} URLs")
    
    # Store results in session for export (make sure it's JSON serializable)
    # Convert complex objects to simple types for session storage
    serializable_results = []
    for result in results:
        # Create a clean copy without any complex objects
        clean_result = {
            'url': result.get('url', ''),
            'robots_url': result.get('robots_url', ''),
            'status': result.get('status', ''),
            'google_disallowed': result.get('google_disallowed', False),
            'robots_content': result.get('robots_content', ''),
            'error_message': result.get('error_message', ''),
            'disallow_rules': []
        }
        
        # Add disallow rules
        for rule in result.get('disallow_rules', []):
            clean_result['disallow_rules'].append({
                'agent': rule.get('agent', ''),
                'rule': rule.get('rule', '')
            })
            
        serializable_results.append(clean_result)
        
    session['last_results'] = serializable_results
    
    return render_template('index.html', results=results, urls_text=urls_text)

# Export functionality
@app.route('/export/<format>')
def export_results(format):
    """Export the analysis results in various formats"""
    results = session.get('last_results', [])
    
    if not results:
        flash('No results to export. Please analyze some URLs first.', 'warning')
        return render_template('index.html')
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format == 'json':
        # Export as JSON
        response = Response(
            json.dumps(results, indent=2),
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment;filename=robots_analysis_{timestamp}.json'}
        )
        return response
        
    elif format == 'csv':
        # Export as CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'URL', 
            'Status', 
            'Google Allowed', 
            'Disallow Rules Count',
            'Robots.txt URL',
            'Error Message',
            'Top Disallow Rules'
        ])
        
        # Write data
        for result in results:
            google_allowed = 'No' if result.get('google_disallowed', False) else 'Yes'
            disallow_rules = result.get('disallow_rules', [])
            disallow_rules_count = len(disallow_rules)
            
            # Get top 3 rules as a string
            top_rules = ""
            if disallow_rules:
                top_rules = "; ".join([f"{rule.get('agent')}: {rule.get('rule')}" 
                                     for rule in disallow_rules[:3]])
                if len(disallow_rules) > 3:
                    top_rules += f"; ... and {len(disallow_rules) - 3} more"
            
            writer.writerow([
                result.get('url', ''),
                result.get('status', ''),
                google_allowed,
                disallow_rules_count,
                result.get('robots_url', ''),
                result.get('error_message', ''),
                top_rules
            ])
        
        response = Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment;filename=robots_analysis_{timestamp}.csv'}
        )
        return response
        
    elif format == 'txt':
        # Export as plain text
        output = []
        output.append(f"Robots.txt Analysis Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("=" * 80)
        output.append("")
        
        for i, result in enumerate(results, 1):
            output.append(f"{i}. {result.get('url', 'Unknown URL')}")
            output.append(f"   Status: {result.get('status', 'Unknown')}")
            output.append(f"   Google Allowed: {'No' if result.get('google_disallowed', False) else 'Yes'}")
            
            disallow_rules = result.get('disallow_rules', [])
            if disallow_rules:
                output.append(f"   Disallow Rules ({len(disallow_rules)}):")
                for rule in disallow_rules[:10]:  # Limit to first 10 rules
                    output.append(f"     - {rule.get('agent', 'Unknown')}: {rule.get('rule', 'Unknown')}")
                if len(disallow_rules) > 10:
                    output.append(f"     ... and {len(disallow_rules) - 10} more rules")
            else:
                output.append("   No disallow rules for Google")
            
            output.append("")
        
        response = Response(
            "\n".join(output),
            mimetype='text/plain',
            headers={'Content-Disposition': f'attachment;filename=robots_analysis_{timestamp}.txt'}
        )
        return response
    
    else:
        flash(f'Unknown export format: {format}', 'danger')
        return render_template('index.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('index.html', error="Method not allowed. Please use the form to submit URLs."), 405

@app.errorhandler(500)
def server_error(e):
    return render_template('index.html', error="Server error occurred"), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
