"""
DNS resolution and HTTPS probing
"""
import asyncio
import aiohttp
import dns.asyncresolver
from typing import Set, Tuple
from urllib.parse import urljoin
import socket


class SubdomainScanner:
    """
    Scan subdomains with DNS resolution and HTTPS probing
    """
    
    def __init__(self, concurrency: int = 50, timeout: int = 10):
        self.concurrency = concurrency
        self.timeout = timeout
        self.resolver = dns.asyncresolver.Resolver()
        self.resolver.timeout = timeout
        self.resolver.lifetime = timeout
    
    async def resolve_dns(self, subdomain: str) -> bool:
        """
        Resolve subdomain DNS A record
        """
        try:
            # Try A record first
            await self.resolver.resolve(subdomain, 'A')
            return True
        except (dns.asyncresolver.NXDOMAIN, 
                dns.asyncresolver.NoAnswer,
                dns.asyncresolver.Timeout,
                dns.exception.DNSException,
                Exception):
            try:
                # Try CNAME record
                await self.resolver.resolve(subdomain, 'CNAME')
                return True
            except:
                return False
    
    async def check_https(self, subdomain: str) -> bool:
        """
        Check if HTTPS is accessible
        """
        url = f"https://{subdomain}"
        
        connector = aiohttp.TCPConnector(ssl=False, limit=self.concurrency)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        try:
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            ) as session:
                async with session.head(url, allow_redirects=True) as response:
                    return response.status < 400
        except (aiohttp.ClientError, 
                asyncio.TimeoutError,
                socket.gaierror,
                OSError,
                UnicodeDecodeError):
            return False
        finally:
            await connector.close()
    
    async def scan_subdomains(self, subdomains: Set[str]) -> Tuple[Set[str], Set[str]]:
        """
        Scan multiple subdomains concurrently
        """
        https_alive = set()
        dns_resolved = set()
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.concurrency)
        
        async def check_subdomain(subdomain: str):
            async with semaphore:
                # Check DNS first
                if await self.resolve_dns(subdomain):
                    dns_resolved.add(subdomain)
                    # If DNS resolves, check HTTPS
                    if await self.check_https(subdomain):
                        https_alive.add(subdomain)
        
        # Run all checks concurrently
        tasks = [check_subdomain(subdomain) for subdomain in subdomains]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return https_alive, dns_resolved
    
    async def quick_scan(self, subdomains: Set[str]) -> Tuple[Set[str], Set[str]]:
        """
        Quick scan with limited concurrency for faster response
        """
        self.concurrency = 20
        return await self.scan_subdomains(subdomains)


def get_scanner_for_mode(mode: str):
    """
    Get appropriate scanner based on mode
    """
    if mode == 'normal':
        return SubdomainScanner(concurrency=20, timeout=5)
    elif mode == 'medium':
        return SubdomainScanner(concurrency=30, timeout=8)
    else:  # ultimate
        return SubdomainScanner(concurrency=50, timeout=10)
