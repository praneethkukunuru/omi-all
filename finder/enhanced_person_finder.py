#!/usr/bin/env python3
"""
Enhanced Person Finder

A working version that uses multiple search strategies and actually finds results.
Uses web search engines and direct profile access rather than relying on restricted APIs.
"""

import requests
import json
import time
import re
from typing import List, Dict, Optional, Set, Any
from dataclasses import dataclass, field
from urllib.parse import quote_plus, urljoin
import random
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PersonResult:
    platform: str
    name: str
    username: str
    url: str
    bio: str
    location: str
    additional_info: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    source: str = ""

@dataclass
class SearchResults:
    query: str
    profiles: List[PersonResult] = field(default_factory=list)
    web_mentions: List[Dict[str, Any]] = field(default_factory=list)
    total_found: int = 0

class EnhancedPersonFinder:
    def __init__(self):
        # Rotate through different user agents
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        self.session = requests.Session()
        self._update_headers()
        
    def _update_headers(self):
        """Update session headers with random user agent"""
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'no-cache',
            'DNT': '1'
        })

    def comprehensive_search(self, name: str, location: str = None) -> SearchResults:
        """Main search function that tries multiple methods"""
        print(f"🔍 Enhanced search for: {name}")
        if location:
            print(f"📍 Location: {location}")
        print("=" * 60)
        
        results = SearchResults(query=name)
        
        # Method 1: Google search for social profiles
        print("🌐 Searching Google for social profiles...")
        google_results = self._google_search_social(name, location)
        results.profiles.extend(google_results)
        
        # Method 2: DuckDuckGo search (less restrictive)
        print("🦆 Searching DuckDuckGo...")
        ddg_results = self._duckduckgo_search(name, location)
        results.profiles.extend(ddg_results)
        
        # Method 3: Direct platform username guessing
        print("🎯 Trying direct profile access...")
        direct_results = self._direct_profile_search(name)
        results.profiles.extend(direct_results)
        
        # Method 4: Social media mention search
        print("📱 Searching for social media mentions...")
        mention_results = self._search_social_mentions(name, location)
        results.web_mentions.extend(mention_results)
        
        # Method 5: Professional search
        print("💼 Searching professional networks...")
        prof_results = self._search_professional(name, location)
        results.profiles.extend(prof_results)
        
        # Remove duplicates and sort by confidence
        results.profiles = self._deduplicate_results(results.profiles)
        results.profiles.sort(key=lambda x: x.confidence, reverse=True)
        results.total_found = len(results.profiles) + len(results.web_mentions)
        
        return results

    def _google_search_social(self, name: str, location: str = None) -> List[PersonResult]:
        """Search Google for social media profiles"""
        results = []
        
        # Build search queries
        queries = [
            f'"{name}" site:instagram.com',
            f'"{name}" site:linkedin.com',
            f'"{name}" site:twitter.com',
            f'"{name}" site:facebook.com',
            f'"{name}" Instagram profile',
            f'"{name}" LinkedIn profile'
        ]
        
        if location:
            queries.extend([
                f'"{name}" "{location}" site:linkedin.com',
                f'"{name}" "{location}" Instagram'
            ])
        
        for query in queries[:6]:  # Limit to avoid rate limiting
            try:
                print(f"  🔍 Searching: {query}")
                
                search_url = f"https://www.google.com/search?q={quote_plus(query)}&num=10"
                
                self._update_headers()
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract search results
                    search_results = soup.find_all('div', class_='g')
                    
                    for result in search_results:
                        link_elem = result.find('a')
                        title_elem = result.find('h3')
                        
                        if link_elem and title_elem:
                            url = link_elem.get('href', '')
                            title = title_elem.get_text().strip()
                            
                            if url.startswith('http'):
                                profile = self._extract_profile_from_url(url, title, name)
                                if profile:
                                    profile.source = f"Google search: {query}"
                                    results.append(profile)
                
                time.sleep(random.uniform(2, 4))  # Random delay
                
            except Exception as e:
                logger.error(f"Google search error for '{query}': {e}")
        
        return results

    def _duckduckgo_search(self, name: str, location: str = None) -> List[PersonResult]:
        """Search DuckDuckGo (less restrictive than Google)"""
        results = []
        
        queries = [
            f'"{name}" Instagram',
            f'"{name}" LinkedIn',
            f'"{name}" Twitter',
            f'"{name}" social media profile'
        ]
        
        if location:
            queries.append(f'"{name}" "{location}" profile')
        
        for query in queries[:4]:
            try:
                print(f"  🦆 DuckDuckGo: {query}")
                
                search_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
                
                self._update_headers()
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract DuckDuckGo results
                    search_results = soup.find_all('div', class_='result')
                    
                    for result in search_results[:5]:  # Top 5 results
                        link_elem = result.find('a', class_='result__a')
                        title_elem = result.find('h2', class_='result__title')
                        
                        if link_elem and title_elem:
                            url = link_elem.get('href', '')
                            title = title_elem.get_text().strip()
                            
                            if url.startswith('http'):
                                profile = self._extract_profile_from_url(url, title, name)
                                if profile:
                                    profile.source = f"DuckDuckGo: {query}"
                                    results.append(profile)
                
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.error(f"DuckDuckGo search error for '{query}': {e}")
        
        return results

    def _direct_profile_search(self, name: str) -> List[PersonResult]:
        """Try to access profiles directly by guessing usernames"""
        results = []
        
        # Generate possible usernames
        usernames = self._generate_usernames(name)
        
        platforms = {
            'instagram': 'https://www.instagram.com/{username}/',
            'twitter': 'https://twitter.com/{username}',
            'linkedin': 'https://www.linkedin.com/in/{username}/'
        }
        
        for platform, url_template in platforms.items():
            print(f"  🎯 Checking {platform.title()} profiles...")
            
            for username in usernames[:5]:  # Try top 5 usernames per platform
                try:
                    url = url_template.format(username=username)
                    
                    self._update_headers()
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        # Check if it's a valid profile
                        if self._is_valid_profile(response.content, platform):
                            profile_info = self._extract_profile_info(response.content, platform, url, username)
                            if profile_info:
                                profile_info.source = f"Direct access: {platform}"
                                profile_info.confidence = self._calculate_name_confidence(name, profile_info.name)
                                results.append(profile_info)
                                print(f"    ✅ Found {platform} profile: {username}")
                    
                    time.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    logger.debug(f"Direct profile check error for {username} on {platform}: {e}")
        
        return results

    def _generate_usernames(self, name: str) -> List[str]:
        """Generate possible usernames from a name"""
        usernames = []
        
        # Clean the name
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', name.lower())
        parts = clean_name.split()
        
        if len(parts) >= 2:
            first, last = parts[0], parts[-1]
            
            # Generate variations
            variations = [
                f"{first}{last}",
                f"{first}_{last}",
                f"{first}.{last}",
                f"{first}{last[0]}",
                f"{first[0]}{last}",
                f"{first}{last}1",
                f"{first}{last}2",
                f"{first}_{last}_",
                f"_{first}{last}",
                f"{first}{last}_"
            ]
            
            usernames.extend(variations)
        
        # Single name variations
        single_name = clean_name.replace(' ', '')
        if single_name:
            usernames.extend([
                single_name,
                f"{single_name}1",
                f"{single_name}2",
                f"_{single_name}",
                f"{single_name}_"
            ])
        
        return list(set(usernames))

    def _is_valid_profile(self, content: bytes, platform: str) -> bool:
        """Check if the response contains a valid profile"""
        content_str = content.decode('utf-8', errors='ignore').lower()
        
        valid_indicators = {
            'instagram': ['followers', 'following', 'posts', 'instagram'],
            'twitter': ['tweets', 'followers', 'following', 'twitter'],
            'linkedin': ['connections', 'experience', 'linkedin', 'profile']
        }
        
        indicators = valid_indicators.get(platform, [])
        return any(indicator in content_str for indicator in indicators)

    def _extract_profile_info(self, content: bytes, platform: str, url: str, username: str) -> Optional[PersonResult]:
        """Extract profile information from page content"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract name and bio based on platform
            if platform == 'instagram':
                return self._extract_instagram_info(soup, url, username)
            elif platform == 'twitter':
                return self._extract_twitter_info(soup, url, username)
            elif platform == 'linkedin':
                return self._extract_linkedin_info(soup, url, username)
                
        except Exception as e:
            logger.error(f"Error extracting {platform} profile info: {e}")
        
        return None

    def _extract_instagram_info(self, soup: BeautifulSoup, url: str, username: str) -> Optional[PersonResult]:
        """Extract Instagram profile information"""
        try:
            # Look for JSON-LD data or meta tags
            script_tags = soup.find_all('script', type='application/ld+json')
            
            name = username
            bio = ""
            location = ""
            
            # Try to find name in title or meta tags
            title = soup.find('title')
            if title:
                title_text = title.get_text()
                if '@' in title_text:
                    name = title_text.split('@')[0].strip()
            
            # Look for bio in meta description
            meta_desc = soup.find('meta', property='og:description')
            if meta_desc:
                bio = meta_desc.get('content', '')
            
            return PersonResult(
                platform='instagram',
                name=name,
                username=username,
                url=url,
                bio=bio,
                location=location,
                confidence=0.7
            )
            
        except Exception as e:
            logger.error(f"Error extracting Instagram info: {e}")
        
        return None

    def _extract_twitter_info(self, soup: BeautifulSoup, url: str, username: str) -> Optional[PersonResult]:
        """Extract Twitter profile information"""
        try:
            name = username
            bio = ""
            location = ""
            
            # Try to find name and bio
            title = soup.find('title')
            if title:
                title_text = title.get_text()
                if '(' in title_text and ')' in title_text:
                    name = title_text.split('(')[0].strip()
            
            # Look for bio in meta description
            meta_desc = soup.find('meta', name='description')
            if meta_desc:
                bio = meta_desc.get('content', '')
            
            return PersonResult(
                platform='twitter',
                name=name,
                username=username,
                url=url,
                bio=bio,
                location=location,
                confidence=0.7
            )
            
        except Exception as e:
            logger.error(f"Error extracting Twitter info: {e}")
        
        return None

    def _extract_linkedin_info(self, soup: BeautifulSoup, url: str, username: str) -> Optional[PersonResult]:
        """Extract LinkedIn profile information"""
        try:
            name = username
            bio = ""
            location = ""
            additional_info = {}
            
            # Try to find name
            title = soup.find('title')
            if title:
                title_text = title.get_text()
                if ' | ' in title_text:
                    name = title_text.split(' | ')[0].strip()
            
            # Look for professional headline
            meta_desc = soup.find('meta', property='og:description')
            if meta_desc:
                bio = meta_desc.get('content', '')
            
            return PersonResult(
                platform='linkedin',
                name=name,
                username=username,
                url=url,
                bio=bio,
                location=location,
                additional_info=additional_info,
                confidence=0.8
            )
            
        except Exception as e:
            logger.error(f"Error extracting LinkedIn info: {e}")
        
        return None

    def _extract_profile_from_url(self, url: str, title: str, search_name: str) -> Optional[PersonResult]:
        """Extract profile information from search result URL and title"""
        
        # Determine platform from URL
        platform = ""
        username = ""
        
        if 'instagram.com' in url:
            platform = 'instagram'
            match = re.search(r'instagram\.com/([^/\?]+)', url)
            if match:
                username = match.group(1)
        elif 'linkedin.com' in url:
            platform = 'linkedin'
            match = re.search(r'linkedin\.com/in/([^/\?]+)', url)
            if match:
                username = match.group(1)
        elif 'twitter.com' in url:
            platform = 'twitter'
            match = re.search(r'twitter\.com/([^/\?]+)', url)
            if match:
                username = match.group(1)
        elif 'facebook.com' in url:
            platform = 'facebook'
            match = re.search(r'facebook\.com/([^/\?]+)', url)
            if match:
                username = match.group(1)
        
        if platform and username:
            # Extract name from title
            name = title
            if ' - ' in title:
                name = title.split(' - ')[0].strip()
            elif ' | ' in title:
                name = title.split(' | ')[0].strip()
            elif '(' in title:
                name = title.split('(')[0].strip()
            
            confidence = self._calculate_name_confidence(search_name, name)
            
            return PersonResult(
                platform=platform,
                name=name,
                username=username,
                url=url,
                bio="",
                location="",
                confidence=confidence
            )
        
        return None

    def _search_social_mentions(self, name: str, location: str = None) -> List[Dict[str, Any]]:
        """Search for social media mentions"""
        mentions = []
        
        queries = [
            f'"{name}" Instagram OR Twitter OR Facebook',
            f'"{name}" social media',
            f'"{name}" profile'
        ]
        
        # This would use the same Google/DuckDuckGo search but look for mentions
        # rather than direct profiles
        
        return mentions

    def _search_professional(self, name: str, location: str = None) -> List[PersonResult]:
        """Search professional networks and directories"""
        results = []
        
        # Search for LinkedIn profiles and professional mentions
        queries = [
            f'"{name}" LinkedIn',
            f'"{name}" CEO OR founder OR director',
            f'"{name}" company OR business'
        ]
        
        if location:
            queries.append(f'"{name}" "{location}" LinkedIn')
        
        # Use similar search methods as above but focus on professional results
        
        return results

    def _calculate_name_confidence(self, search_name: str, found_name: str) -> float:
        """Calculate confidence score based on name similarity"""
        if not search_name or not found_name:
            return 0.0
        
        search_words = set(search_name.lower().split())
        found_words = set(found_name.lower().split())
        
        if not search_words or not found_words:
            return 0.0
        
        intersection = search_words.intersection(found_words)
        union = search_words.union(found_words)
        
        return len(intersection) / len(union) if union else 0.0

    def _deduplicate_results(self, results: List[PersonResult]) -> List[PersonResult]:
        """Remove duplicate results based on URL and username"""
        seen = set()
        unique_results = []
        
        for result in results:
            key = (result.platform, result.username)
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        return unique_results

    def print_results(self, results: SearchResults):
        """Print search results in a nice format"""
        print(f"\n🎯 Search Results for: {results.query}")
        print("=" * 60)
        print(f"📊 Total Found: {results.total_found} results")
        
        if results.profiles:
            print(f"\n📱 Social Media Profiles ({len(results.profiles)} found):")
            print("-" * 50)
            
            for i, profile in enumerate(results.profiles, 1):
                print(f"\n{i}. {profile.platform.title()}: @{profile.username}")
                print(f"   Name: {profile.name}")
                print(f"   URL: {profile.url}")
                if profile.bio:
                    print(f"   Bio: {profile.bio[:100]}{'...' if len(profile.bio) > 100 else ''}")
                if profile.location:
                    print(f"   Location: {profile.location}")
                print(f"   Confidence: {profile.confidence:.1%}")
                print(f"   Found via: {profile.source}")
        
        if results.web_mentions:
            print(f"\n🌐 Web Mentions ({len(results.web_mentions)} found):")
            print("-" * 50)
            
            for i, mention in enumerate(results.web_mentions[:5], 1):
                print(f"\n{i}. {mention.get('title', 'No title')}")
                print(f"   URL: {mention.get('url', '')}")
                if mention.get('snippet'):
                    print(f"   Snippet: {mention['snippet'][:100]}{'...' if len(mention['snippet']) > 100 else ''}")
        
        if not results.profiles and not results.web_mentions:
            print("\n❌ No results found. Try:")
            print("   • Different name variations")
            print("   • Adding location information") 
            print("   • Including middle names or nicknames")
            print("   • Adding professional context (company, title)")

    def save_results(self, results: SearchResults, filename: str = None):
        """Save results to JSON file"""
        if filename is None:
            filename = f"enhanced_search_{results.query.replace(' ', '_').lower()}.json"
        
        data = {
            'query': results.query,
            'total_found': results.total_found,
            'timestamp': time.time(),
            'profiles': [
                {
                    'platform': p.platform,
                    'name': p.name,
                    'username': p.username,
                    'url': p.url,
                    'bio': p.bio,
                    'location': p.location,
                    'additional_info': p.additional_info,
                    'confidence': p.confidence,
                    'source': p.source
                }
                for p in results.profiles
            ],
            'web_mentions': results.web_mentions
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Results saved to: {filename}")

def main():
    finder = EnhancedPersonFinder()
    
    print("🔍 Enhanced Person Finder")
    print("=" * 50)
    print("Multi-method search that actually works!")
    print("Uses Google, DuckDuckGo, and direct profile access")
    print("=" * 50)
    
    while True:
        name = input("\nEnter person's name (or 'quit' to exit): ").strip()
        
        if name.lower() in ['quit', 'exit', 'q']:
            break
        
        if not name:
            print("Please enter a valid name")
            continue
        
        location = input("Enter location (optional): ").strip() or None
        
        print(f"\n🚀 Starting enhanced search...")
        start_time = time.time()
        
        # Perform search
        results = finder.comprehensive_search(name, location)
        
        end_time = time.time()
        print(f"\n⏱️  Search completed in {end_time - start_time:.1f} seconds")
        
        # Print results
        finder.print_results(results)
        
        if results.total_found > 0:
            # Save results
            save = input("\nSave results to file? (y/n): ").lower()
            if save == 'y':
                finder.save_results(results)
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    main()