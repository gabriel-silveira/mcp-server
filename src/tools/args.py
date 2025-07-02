from typing import Dict, Any

def get_firecrawl_scrape_args(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get cleaned arguments for firecrawl_scrape tool"""
    clean_args = {k: v for k, v in arguments.items() if v is not None}
    
    # Set scrape specific defaults
    if 'formats' not in clean_args:
        clean_args['formats'] = ['markdown']
    if 'timeout' not in clean_args:
        clean_args['timeout'] = 30000
    
    return clean_args

def get_gmail_sendemail_args(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get cleaned arguments for Gmail SendEmail tool"""
    clean_args = {k: v for k, v in arguments.items() if v is not None}
    
    # Set SendEmail specific defaults
    if 'cc' not in clean_args:
        clean_args['cc'] = []
    if 'bcc' not in clean_args:
        clean_args['bcc'] = []
    
    return clean_args

def get_default_args(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get cleaned arguments for any tool without specific defaults"""
    return {k: v for k, v in arguments.items() if v is not None}
