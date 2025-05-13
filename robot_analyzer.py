import re
import logging
import urllib.robotparser
import urllib.parse
import requests
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import RequestException

# Set up logging
logger = logging.getLogger(__name__)

def normalize_url(url):
    """Normalize URL to ensure it has a scheme and is properly formatted"""
    # Add http:// if no scheme is specified
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    # Ensure URL ends with a trailing slash
    parsed_url = urllib.parse.urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    return base_url

def get_robots_txt_url(base_url):
    """Generate the robots.txt URL from a base URL"""
    return urllib.parse.urljoin(base_url, '/robots.txt')

def analyze_robots_txt(url):
    """
    Analyze a robots.txt file to check for Google crawler disallow rules
    
    Args:
        url (str): The website URL to analyze
    
    Returns:
        dict: Results of the analysis including status, disallow rules, etc.
    """
    try:
        # Normalize the URL
        base_url = normalize_url(url)
        robots_url = get_robots_txt_url(base_url)
        
        logger.debug(f"Analyzing robots.txt for {base_url}")
        logger.debug(f"Robots.txt URL: {robots_url}")
        
        # Fetch the robots.txt file
        response = requests.get(robots_url, timeout=15)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        robots_content = response.text
        
        # Use robotparser to parse the file
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.parse(robots_content.splitlines())
        
        # Check for Google user agents
        google_agents = [
            'Googlebot',
            'Googlebot-Image',
            'Googlebot-Mobile',
            'Googlebot-News',
            'Googlebot-Video',
            'Google',
            'AdsBot-Google',
            'AdsBot-Google-Mobile',
            'APIs-Google',
            'DuplexWeb-Google',
            'FeedFetcher-Google',
            'Google-Read-Aloud',
            'Mediapartners-Google',
            'Storebot-Google'
        ]
        
        disallow_rules = []
        google_disallowed = False
        
        # Extract disallow rules for Google user agents using regex
        for agent in google_agents:
            # First check using robotparser
            if not rp.can_fetch(agent, base_url):
                google_disallowed = True
            
            # Also manually check the robots.txt content to catch all rules
            agent_pattern = re.compile(rf'User-agent:[ \t]*{re.escape(agent)}', re.IGNORECASE)
            disallow_pattern = re.compile(r'Disallow:[ \t]*([^\n#]*)', re.IGNORECASE)
            
            # Find all blocks for this user agent
            for match in agent_pattern.finditer(robots_content):
                start_pos = match.end()
                # Find the next User-agent declaration or end of file
                next_agent = agent_pattern.search(robots_content, start_pos)
                end_pos = next_agent.start() if next_agent else len(robots_content)
                
                # Get block of text for this user agent
                block = robots_content[start_pos:end_pos]
                
                # Find all disallow rules in this block
                for disallow_match in disallow_pattern.finditer(block):
                    rule = disallow_match.group(1).strip()
                    if rule and rule != '/':  # Ignore empty rules or just "/"
                        disallow_rules.append({
                            'agent': agent,
                            'rule': rule
                        })
                        google_disallowed = True
        
        return {
            'url': url,
            'robots_url': robots_url,
            'status': 'success',
            'google_disallowed': google_disallowed,
            'disallow_rules': disallow_rules,
            'robots_content': robots_content
        }
        
    except RequestException as e:
        logger.error(f"Error fetching robots.txt for {url}: {str(e)}")
        error_msg = f"Failed to fetch robots.txt: {str(e)}"
        if "timeout" in str(e).lower():
            error_msg = "Connection timed out (15s limit). Site may be slow or unresponsive."
        return {
            'url': url,
            'status': 'error',
            'error_message': error_msg,
            'google_disallowed': False,
            'disallow_rules': []
        }
    except Exception as e:
        logger.error(f"Error analyzing robots.txt for {url}: {str(e)}")
        return {
            'url': url,
            'status': 'error',
            'error_message': f"Failed to analyze robots.txt: {str(e)}",
            'google_disallowed': False,
            'disallow_rules': []
        }

def analyze_robots_txt_urls(urls, max_workers=25):
    """
    Analyze multiple robots.txt files concurrently
    
    Args:
        urls (list): List of URLs to analyze
        max_workers (int): Maximum number of concurrent workers
        
    Returns:
        list: Results for each URL
    """
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks and collect futures
        future_to_url = {executor.submit(analyze_robots_txt, url): url for url in urls}
        
        # Process results as they complete
        for future in future_to_url:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                url = future_to_url[future]
                logger.error(f"Unexpected error processing {url}: {str(e)}")
                results.append({
                    'url': url,
                    'status': 'error',
                    'error_message': f"Unexpected error: {str(e)}",
                    'google_disallowed': False,
                    'disallow_rules': []
                })
    
    return results
