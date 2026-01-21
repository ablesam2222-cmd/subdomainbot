"""
Utility functions for the subdomain enumeration bot
"""
import os
import re
import json
import asyncio
from typing import Set, Dict, List, Tuple
from datetime import datetime
from pathlib import Path


def validate_domain(domain: str) -> bool:
    """
    Validate domain format
    """
    # Basic validation: at least one dot, no spaces
    if not domain or ' ' in domain:
        return False
    
    # Remove protocol if present
    domain = domain.lower().strip()
    if domain.startswith(('http://', 'https://')):
        domain = domain.split('://')[1]
    
    # Remove paths
    domain = domain.split('/')[0]
    
    # Check for at least one dot and valid characters
    pattern = r'^[a-z0-9.-]+\.[a-z]{2,}$'
    return bool(re.match(pattern, domain)) and domain.count('.') >= 1


def format_results(https_alive: Set[str], dns_resolved: Set[str]) -> str:
    """
    Format scan results into a readable string
    """
    total_https = len(https_alive)
    total_dns = len(dns_resolved)
    
    output = [
        f"═" * 40,
        f"📊 SCAN RESULTS SUMMARY",
        f"═" * 40,
        f"🟢 HTTPS Alive: {total_https} subdomains",
        f"🔵 DNS Resolved: {total_dns} subdomains",
        f"═" * 40,
    ]
    
    if https_alive:
        output.append("\n🔐 HTTPS ALIVE SUBDOMAINS:")
        for subdomain in sorted(https_alive):
            output.append(f"  ✅ https://{subdomain}")
    
    if dns_resolved - https_alive:
        output.append("\n🌐 DNS ONLY SUBDOMAINS:")
        for subdomain in sorted(dns_resolved - https_alive):
            output.append(f"  📡 {subdomain}")
    
    return "\n".join(output)


def save_results_to_file(domain: str, https_alive: Set[str], 
                         dns_resolved: Set[str]) -> str:
    """
    Save results to a text file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"subdomain_scan_{domain}_{timestamp}.txt"
    
    results_dir = Path("scan_results")
    results_dir.mkdir(exist_ok=True)
    
    filepath = results_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Subdomain Enumeration Results for {domain}\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write("═" * 50 + "\n\n")
        
        f.write(f"HTTPS Alive ({len(https_alive)}):\n")
        f.write("─" * 30 + "\n")
        for subdomain in sorted(https_alive):
            f.write(f"https://{subdomain}\n")
        
        f.write(f"\nDNS Resolved ({len(dns_resolved)}):\n")
        f.write("─" * 30 + "\n")
        for subdomain in sorted(dns_resolved):
            f.write(f"{subdomain}\n")
    
    return str(filepath)


class UserSession:
    """
    Store user session data
    """
    def __init__(self):
        self.sessions: Dict[int, Dict] = {}
    
    def create(self, user_id: int) -> Dict:
        """Create a new session"""
        self.sessions[user_id] = {
            'domain': None,
            'mode': None,
            'candidates': set(),
            'https_alive': set(),
            'dns_resolved': set(),
            'scanning': False
        }
        return self.sessions[user_id]
    
    def get(self, user_id: int) -> Dict:
        """Get user session"""
        return self.sessions.get(user_id)
    
    def update(self, user_id: int, **kwargs):
        """Update session data"""
        if user_id in self.sessions:
            self.sessions[user_id].update(kwargs)
    
    def delete(self, user_id: int):
        """Delete user session"""
        self.sessions.pop(user_id, None)


# Initialize global session manager
user_session = UserSession()
