"""
Generate candidate subdomains using AI-style heuristics
"""
import itertools
from typing import Set, List


class SubdomainGenerator:
    """
    Generate subdomain candidates using various heuristics
    """
    
    # Common subdomain prefixes
    COMMON_PREFIXES = [
        'www', 'mail', 'ftp', 'smtp', 'pop', 'imap', 'webmail',
        'admin', 'administrator', 'login', 'dashboard', 'panel',
        'api', 'api2', 'api3', 'vpn', 'remote', 'ssh',
        'dev', 'development', 'staging', 'test', 'qa',
        'blog', 'news', 'forum', 'support', 'help', 'docs',
        'app', 'apps', 'application', 'portal', 'hub',
        'static', 'assets', 'cdn', 'media', 'images', 'img',
        'shop', 'store', 'ecommerce', 'payment', 'pay',
        'm', 'mobile', 'wap', 'i', 'iphone',
        'secure', 'ssl', 'safe', 'private',
        'cpanel', 'whm', 'webdisk', 'webhost',
        'ns1', 'ns2', 'ns3', 'dns', 'mx', 'mx1', 'mx2',
        'git', 'svn', 'repo', 'code',
        'status', 'monitor', 'monitoring', 'metrics',
        'db', 'database', 'sql', 'mysql', 'postgres',
    ]
    
    # Environment suffixes
    ENVIRONMENTS = ['dev', 'test', 'staging', 'prod', 'production', 'uat', 'qa']
    
    # Geographic prefixes
    GEO_PREFIXES = ['us', 'uk', 'eu', 'de', 'fr', 'jp', 'sg', 'au', 'in']
    
    # Number patterns
    NUMERIC_PATTERNS = [
        '', '1', '2', '3', '01', '02', '03', 
        '2023', '2024', '2025', '2026',
        '01', '02', '03', '04', '05', '06', '07', '08', '09', '10'
    ]
    
    @classmethod
    def generate_candidates(cls, domain: str, mode: str = 'normal') -> Set[str]:
        """
        Generate subdomain candidates based on mode
        """
        candidates = set()
        
        # Remove www. if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Base candidates - always include
        base_candidates = [
            f"www.{domain}",
            f"mail.{domain}",
            f"api.{domain}",
            f"admin.{domain}",
            f"blog.{domain}",
            f"dev.{domain}",
            f"staging.{domain}",
            f"test.{domain}",
            f"mobile.{domain}",
            f"static.{domain}",
            f"cdn.{domain}",
            f"portal.{domain}",
            f"app.{domain}",
            f"secure.{domain}",
            f"vpn.{domain}",
            f"m.{domain}",
            f"old.{domain}",
            f"new.{domain}",
        ]
        
        candidates.update(base_candidates)
        
        # Add common prefixes
        for prefix in cls.COMMON_PREFIXES:
            candidates.add(f"{prefix}.{domain}")
        
        # NORMAL mode - basic combinations
        if mode == 'normal':
            # Add some environment combinations
            for env in cls.ENVIRONMENTS[:3]:
                candidates.add(f"{env}.{domain}")
                candidates.add(f"{env}-web.{domain}")
            
            # Add some numeric suffixes
            for num in ['1', '2', '3', '01', '02']:
                candidates.add(f"web{num}.{domain}")
                candidates.add(f"app{num}.{domain}")
                candidates.add(f"api{num}.{domain}")
        
        # MEDIUM mode - more combinations
        elif mode == 'medium':
            # Environment combinations
            for env in cls.ENVIRONMENTS:
                candidates.add(f"{env}.{domain}")
                candidates.add(f"{env}-web.{domain}")
                candidates.add(f"web-{env}.{domain}")
                candidates.add(f"{env}-app.{domain}")
            
            # Geographic prefixes
            for geo in cls.GEO_PREFIXES:
                candidates.add(f"{geo}.{domain}")
                candidates.add(f"{geo}-web.{domain}")
                candidates.add(f"www-{geo}.{domain}")
            
            # More numeric patterns
            for i in range(1, 11):
                candidates.add(f"web{i:02d}.{domain}")
                candidates.add(f"app{i:02d}.{domain}")
                candidates.add(f"api{i:02d}.{domain}")
                candidates.add(f"server{i:02d}.{domain}")
        
        # ULTIMATE mode - comprehensive combinations
        elif mode == 'ultimate':
            # Extensive environment combinations
            for env in cls.ENVIRONMENTS:
                for prefix in ['', 'www-', 'web-', 'app-', 'api-']:
                    candidates.add(f"{prefix}{env}.{domain}")
                    for num in ['', '1', '2', '3']:
                        candidates.add(f"{prefix}{env}{num}.{domain}")
            
            # Geographic + environment combinations
            for geo in cls.GEO_PREFIXES:
                for env in cls.ENVIRONMENTS[:4]:
                    candidates.add(f"{geo}-{env}.{domain}")
                    candidates.add(f"{env}-{geo}.{domain}")
            
            # Multi-level subdomains
            for prefix1 in ['app', 'web', 'api', 'service']:
                for prefix2 in cls.ENVIRONMENTS[:3]:
                    candidates.add(f"{prefix1}-{prefix2}.{domain}")
                    for num in ['', '1', '2']:
                        candidates.add(f"{prefix1}{num}-{prefix2}.{domain}")
            
            # Extensive numeric patterns
            for i in range(1, 21):
                for prefix in ['web', 'app', 'api', 'server', 'node', 'host']:
                    candidates.add(f"{prefix}{i:02d}.{domain}")
                    candidates.add(f"{prefix}-{i:02d}.{domain}")
            
            # Special patterns
            special_patterns = [
                f"alpha.{domain}", f"beta.{domain}", f"gamma.{domain}",
                f"prod-{domain.replace('.', '-')}.{domain}",
                f"internal.{domain}", f"external.{domain}",
                f"legacy.{domain}", f"modern.{domain}",
                f"cloud.{domain}", f"aws.{domain}", f"azure.{domain}",
                f"office.{domain}", f"home.{domain}", f"remote.{domain}",
            ]
            candidates.update(special_patterns)
        
        # Generate permutations for common prefixes (limited for performance)
        if mode in ['medium', 'ultimate']:
            # Generate some permutations of common words
            common_words = ['admin', 'api', 'web', 'app', 'dev', 'test']
            
            if mode == 'medium':
                max_combinations = 2
            else:  # ultimate
                max_combinations = 3
            
            # Generate word combinations
            for i in range(2, min(max_combinations + 1, len(common_words) + 1)):
                for combo in itertools.combinations(common_words, i):
                    for perm in itertools.permutations(combo):
                        if mode == 'ultimate' or len(perm) <= 2:
                            candidates.add(f"{'-'.join(perm)}.{domain}")
        
        return candidates
    
    @classmethod
    def estimate_count(cls, mode: str) -> int:
        """
        Estimate number of candidates for each mode
        """
        estimates = {
            'normal': 50,
            'medium': 150,
            'ultimate': 500
        }
        return estimates.get(mode, 50)
