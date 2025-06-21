#!/usr/bin/env python3
"""
Comprehensive Person Finder

Advanced person search that aggregates information from multiple sources:
- LinkedIn profiles and professional information
- Instagram, Twitter, Facebook social media
- Web mentions and articles
- Public records and directories
- Professional networks and associations
- News articles and press mentions
"""

import requests
import json
import time
import re
from typing import List, Dict, Optional, Set, Any
from dataclasses import dataclass, field
from urllib.parse import quote_plus, urlparse, urljoin
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PersonProfile:
    platform: str
    username: str
    full_name: str
    bio: str
    location: str
    followers: int
    following: int
    posts: int
    verified: bool
    private: bool
    url: str
    profile_image: str
    additional_info: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    last_updated: float = field(default_factory=time.time)

@dataclass
class WebMention:
    url: str
    title: str
    snippet: str
    source: str
    date: str
    relevance_score: float
    mention_type: str  # 'article', 'social', 'directory', 'professional'

@dataclass
class PersonData:
    name: str
    profiles: List[PersonProfile] = field(default_factory=list)
    web_mentions: List[WebMention] = field(default_factory=list)
    professional_info: Dict[str, Any] = field(default_factory=dict)
    contact_info: Dict[str, str] = field(default_factory=dict)
    associations: List[str] = field(default_factory=list)
    education: List[Dict[str, str]] = field(default_factory=list)
    work_history: List[Dict[str, str]] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    locations: Set[str] = field(default_factory=set)
    confidence_score: float = 0.0

class ComprehensivePersonFinder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Platform endpoints
        self.endpoints = {
            'instagram': {
                'search': 'https://www.instagram.com/web/search/topsearch/',
                'profile': 'https://www.instagram.com/{username}/'
            },
            'linkedin': {
                'search': 'https://www.linkedin.com/search/results/people/',
                'profile': 'https://www.linkedin.com/in/{username}/'
            },
            'twitter': {
                'search': 'https://twitter.com/search',
                'profile': 'https://twitter.com/{username}'
            },
            'facebook': {
                'search': 'https://www.facebook.com/search/people/',
                'profile': 'https://www.facebook.com/{username}'
            }
        }
        
        # Web search engines
        self.search_engines = [
            'https://www.google.com/search?q={query}',
            'https://duckduckgo.com/?q={query}',
            'https://www.bing.com/search?q={query}'
        ]
        
        self.lock = threading.Lock()
        
    def comprehensive_search(self, name: str, location: str = None, additional_info: str = None) -> PersonData:
        """Main search function that aggregates all information"""
        print(f"🔍 Comprehensive search for: {name}")
        if location:
            print(f"📍 Location: {location}")
        if additional_info:
            print(f"ℹ️  Additional info: {additional_info}")
        print("=" * 60)
        
        person_data = PersonData(name=name)
        
        # Build search queries
        search_queries = self._build_search_queries(name, location, additional_info)
        
        # Use ThreadPoolExecutor for parallel searches
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            # Search social media platforms
            for platform in ['instagram', 'linkedin', 'twitter', 'facebook']:
                future = executor.submit(self._search_platform, platform, search_queries)
                futures.append(('platform', platform, future))
            
            # Search web mentions
            future = executor.submit(self._search_web_mentions, search_queries)
            futures.append(('web', 'mentions', future))
            
            # Search professional directories
            future = executor.submit(self._search_professional_directories, search_queries)
            futures.append(('professional', 'directories', future))
            
            # Search news and articles
            future = executor.submit(self._search_news_articles, search_queries)
            futures.append(('news', 'articles', future))
            
            # Process results as they complete
            for search_type, source, future in futures:
                try:
                    result = future.result(timeout=30)
                    
                    if search_type == 'platform':
                        person_data.profiles.extend(result)
                    elif search_type == 'web':
                        person_data.web_mentions.extend(result)
                    elif search_type == 'professional':
                        self._merge_professional_info(person_data, result)
                    elif search_type == 'news':
                        person_data.web_mentions.extend(result)
                        
                except Exception as e:
                    logger.error(f"Error in {search_type} search for {source}: {e}")
        
        # Post-process and analyze data
        self._analyze_and_correlate_data(person_data)
        
        return person_data
    
    def _build_search_queries(self, name: str, location: str = None, additional_info: str = None) -> List[str]:
        """Build comprehensive search queries"""
        queries = []
        
        # Basic queries
        queries.extend([
            f'"{name}"',
            name,
            name.replace(' ', '+'),
        ])
        
        # Location-based queries
        if location:
            queries.extend([
                f'"{name}" {location}',
                f'"{name}" "{location}"',
                f'{name} {location}'
            ])
        
        # Professional queries
        queries.extend([
            f'"{name}" LinkedIn',
            f'"{name}" profile',
            f'"{name}" professional',
            f'"{name}" CEO OR director OR manager OR founder',
            f'"{name}" company OR organization OR business'
        ])
        
        # Social media queries
        queries.extend([
            f'"{name}" Instagram',
            f'"{name}" Twitter',
            f'"{name}" Facebook',
            f'"{name}" social media'
        ])
        
        # Additional info queries
        if additional_info:
            queries.extend([
                f'"{name}" "{additional_info}"',
                f'{name} {additional_info}'
            ])
        
        return list(set(queries))
    
    def _search_platform(self, platform: str, queries: List[str]) -> List[PersonProfile]:
        """Search a specific platform"""
        print(f"🔍 Searching {platform.title()}...")
        profiles = []
        
        try:
            if platform == 'instagram':
                profiles = self._search_instagram(queries)
            elif platform == 'linkedin':
                profiles = self._search_linkedin(queries)
            elif platform == 'twitter':
                profiles = self._search_twitter(queries)
            elif platform == 'facebook':
                profiles = self._search_facebook(queries)
            
            print(f"✅ Found {len(profiles)} profiles on {platform.title()}")
            
        except Exception as e:
            logger.error(f"Error searching {platform}: {e}")
        
        return profiles
    
    def _search_instagram(self, queries: List[str]) -> List[PersonProfile]:
        """Search Instagram profiles"""
        profiles = []
        
        for query in queries[:3]:  # Limit queries to avoid rate limiting
            try:
                params = {
                    'query': query,
                    'context': 'blended'
                }
                
                headers = self.session.headers.copy()
                headers.update({
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': 'https://www.instagram.com/',
                    'X-IG-App-ID': '936619743392459',
                })
                
                response = self.session.get(
                    self.endpoints['instagram']['search'], 
                    params=params, 
                    headers=headers, 
                    timeout=15
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        users = data.get('users', [])
                        
                        for user_data in users[:10]:
                            user = user_data.get('user', {})
                            if user and user.get('username'):
                                profile = PersonProfile(
                                    platform='instagram',
                                    username=user.get('username', ''),
                                    full_name=user.get('full_name', ''),
                                    bio=user.get('biography', ''),
                                    location='',
                                    followers=user.get('follower_count', 0),
                                    following=user.get('following_count', 0),
                                    posts=user.get('media_count', 0),
                                    verified=user.get('is_verified', False),
                                    private=user.get('is_private', False),
                                    url=f"https://instagram.com/{user.get('username', '')}",
                                    profile_image=user.get('profile_pic_url', ''),
                                    confidence=self._calculate_name_similarity(query, user.get('full_name', ''))
                                )
                                profiles.append(profile)
                                
                    except json.JSONDecodeError:
                        pass
                        
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Instagram search error for '{query}': {e}")
        
        return profiles
    
    def _search_linkedin(self, queries: List[str]) -> List[PersonProfile]:
        """Search LinkedIn profiles"""
        profiles = []
        
        for query in queries[:3]:
            try:
                # LinkedIn search via web scraping
                search_url = f"https://www.linkedin.com/search/results/people/?keywords={quote_plus(query)}"
                
                headers = self.session.headers.copy()
                headers.update({
                    'Referer': 'https://www.linkedin.com/',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                })
                
                response = self.session.get(search_url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract LinkedIn profiles from search results
                    profile_links = soup.find_all('a', href=re.compile(r'/in/[\w-]+'))
                    
                    for link in profile_links[:5]:  # Limit results
                        href = link.get('href')
                        if href and '/in/' in href:
                            username = href.split('/in/')[-1].split('/')[0].split('?')[0]
                            
                            # Try to extract profile info
                            profile_info = self._get_linkedin_profile_info(username)
                            if profile_info:
                                profiles.append(profile_info)
                
                time.sleep(2)  # LinkedIn is more strict about rate limiting
                
            except Exception as e:
                logger.error(f"LinkedIn search error for '{query}': {e}")
        
        return profiles
    
    def _get_linkedin_profile_info(self, username: str) -> Optional[PersonProfile]:
        """Get detailed LinkedIn profile information"""
        try:
            profile_url = f"https://www.linkedin.com/in/{username}/"
            
            headers = self.session.headers.copy()
            headers.update({
                'Referer': 'https://www.linkedin.com/',
            })
            
            response = self.session.get(profile_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract basic info
                name_elem = soup.find('h1', class_=re.compile(r'text-heading-xlarge'))
                name = name_elem.get_text().strip() if name_elem else username
                
                # Extract headline/bio
                headline_elem = soup.find('div', class_=re.compile(r'text-body-medium'))
                headline = headline_elem.get_text().strip() if headline_elem else ''
                
                # Extract location
                location_elem = soup.find('span', class_=re.compile(r'text-body-small'))
                location = location_elem.get_text().strip() if location_elem else ''
                
                # Create profile
                profile = PersonProfile(
                    platform='linkedin',
                    username=username,
                    full_name=name,
                    bio=headline,
                    location=location,
                    followers=0,  # LinkedIn doesn't show follower counts publicly
                    following=0,
                    posts=0,
                    verified=False,
                    private=False,
                    url=profile_url,
                    profile_image='',
                    confidence=0.8
                )
                
                # Extract additional professional info
                profile.additional_info = self._extract_linkedin_details(soup)
                
                return profile
                
        except Exception as e:
            logger.error(f"Error getting LinkedIn profile for {username}: {e}")
        
        return None
    
    def _extract_linkedin_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract detailed information from LinkedIn profile"""
        details = {}
        
        try:
            # Extract experience
            experience_section = soup.find('section', {'data-section': 'experience'})
            if experience_section:
                jobs = []
                job_elements = experience_section.find_all('div', class_=re.compile(r'experience-item'))
                for job in job_elements[:5]:  # Limit to recent jobs
                    job_title = job.find('h3')
                    company = job.find('h4')
                    if job_title and company:
                        jobs.append({
                            'title': job_title.get_text().strip(),
                            'company': company.get_text().strip()
                        })
                details['work_history'] = jobs
            
            # Extract education
            education_section = soup.find('section', {'data-section': 'education'})
            if education_section:
                schools = []
                school_elements = education_section.find_all('div', class_=re.compile(r'education-item'))
                for school in school_elements[:3]:
                    school_name = school.find('h3')
                    degree = school.find('h4')
                    if school_name:
                        schools.append({
                            'school': school_name.get_text().strip(),
                            'degree': degree.get_text().strip() if degree else ''
                        })
                details['education'] = schools
            
            # Extract skills
            skills_section = soup.find('section', {'data-section': 'skills'})
            if skills_section:
                skill_elements = skills_section.find_all('span', class_=re.compile(r'skill-name'))
                skills = [skill.get_text().strip() for skill in skill_elements[:10]]
                details['skills'] = skills
                
        except Exception as e:
            logger.error(f"Error extracting LinkedIn details: {e}")
        
        return details
    
    def _search_twitter(self, queries: List[str]) -> List[PersonProfile]:
        """Search Twitter profiles"""
        profiles = []
        
        # Twitter search is more complex due to their API restrictions
        # This is a simplified version that would need proper Twitter API access
        for query in queries[:2]:
            try:
                # Use web scraping approach (Note: Twitter heavily rate limits this)
                search_url = f"https://twitter.com/search?q={quote_plus(query)}&src=typed_query&f=user"
                
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    # Extract Twitter profiles from search results
                    # This would need more sophisticated parsing
                    pass
                
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Twitter search error for '{query}': {e}")
        
        return profiles
    
    def _search_facebook(self, queries: List[str]) -> List[PersonProfile]:
        """Search Facebook profiles"""
        profiles = []
        
        # Facebook search is very restricted
        # This would typically require Facebook Graph API access
        
        return profiles
    
    def _search_web_mentions(self, queries: List[str]) -> List[WebMention]:
        """Search for web mentions across search engines"""
        print("🌐 Searching web mentions...")
        mentions = []
        
        for query in queries[:5]:  # Limit queries
            try:
                # Use Google search (simplified)
                search_url = f"https://www.google.com/search?q={quote_plus(query)}"
                
                headers = self.session.headers.copy()
                headers.update({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                })
                
                response = self.session.get(search_url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract search results
                    results = soup.find_all('div', class_='g')
                    
                    for result in results[:10]:  # Top 10 results
                        link_elem = result.find('a')
                        title_elem = result.find('h3')
                        snippet_elem = result.find('span', class_=re.compile(r'st|s3v9rd'))
                        
                        if link_elem and title_elem:
                            url = link_elem.get('href', '')
                            title = title_elem.get_text().strip()
                            snippet = snippet_elem.get_text().strip() if snippet_elem else ''
                            
                            if url.startswith('http'):
                                mention = WebMention(
                                    url=url,
                                    title=title,
                                    snippet=snippet,
                                    source='google',
                                    date='',
                                    relevance_score=self._calculate_relevance_score(query, title, snippet),
                                    mention_type=self._classify_mention_type(url, title, snippet)
                                )
                                mentions.append(mention)
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Web search error for '{query}': {e}")
        
        return mentions
    
    def _search_professional_directories(self, queries: List[str]) -> Dict[str, Any]:
        """Search professional directories and business listings"""
        print("💼 Searching professional directories...")
        professional_info = {}
        
        # This would search sites like:
        # - Crunchbase
        # - AngelList
        # - Bloomberg
        # - Reuters
        # - Professional associations
        
        return professional_info
    
    def _search_news_articles(self, queries: List[str]) -> List[WebMention]:
        """Search for news articles and press mentions"""
        print("📰 Searching news articles...")
        articles = []
        
        # This would search news sites and press release sites
        
        return articles
    
    def _calculate_name_similarity(self, query: str, name: str) -> float:
        """Calculate similarity between search query and found name"""
        if not query or not name:
            return 0.0
        
        query_clean = re.sub(r'[^a-zA-Z0-9\s]', '', query.lower())
        name_clean = re.sub(r'[^a-zA-Z0-9\s]', '', name.lower())
        
        # Simple similarity calculation
        query_words = set(query_clean.split())
        name_words = set(name_clean.split())
        
        if not query_words or not name_words:
            return 0.0
        
        intersection = query_words.intersection(name_words)
        union = query_words.union(name_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_relevance_score(self, query: str, title: str, snippet: str) -> float:
        """Calculate relevance score for a web mention"""
        text = f"{title} {snippet}".lower()
        query_words = query.lower().split()
        
        score = 0.0
        for word in query_words:
            if word in text:
                score += 1.0
        
        return score / len(query_words) if query_words else 0.0
    
    def _classify_mention_type(self, url: str, title: str, snippet: str) -> str:
        """Classify the type of web mention"""
        url_lower = url.lower()
        text_lower = f"{title} {snippet}".lower()
        
        if any(site in url_lower for site in ['linkedin', 'facebook', 'twitter', 'instagram']):
            return 'social'
        elif any(word in text_lower for word in ['ceo', 'founder', 'director', 'company', 'business']):
            return 'professional'
        elif any(site in url_lower for site in ['news', 'article', 'press', 'media']):
            return 'article'
        else:
            return 'directory'
    
    def _merge_professional_info(self, person_data: PersonData, professional_info: Dict[str, Any]):
        """Merge professional information into person data"""
        person_data.professional_info.update(professional_info)
    
    def _analyze_and_correlate_data(self, person_data: PersonData):
        """Analyze and correlate all collected data"""
        print("🔍 Analyzing and correlating data...")
        
        # Extract common locations
        for profile in person_data.profiles:
            if profile.location:
                person_data.locations.add(profile.location)
        
        # Extract skills and interests from profiles
        all_skills = set()
        all_interests = set()
        
        for profile in person_data.profiles:
            if 'skills' in profile.additional_info:
                all_skills.update(profile.additional_info['skills'])
            
            # Extract interests from bios
            if profile.bio:
                interests = self._extract_interests_from_text(profile.bio)
                all_interests.update(interests)
        
        person_data.skills = list(all_skills)
        person_data.interests = list(all_interests)
        
        # Calculate overall confidence score
        if person_data.profiles:
            avg_confidence = sum(p.confidence for p in person_data.profiles) / len(person_data.profiles)
            person_data.confidence_score = avg_confidence
        
        # Sort profiles by confidence
        person_data.profiles.sort(key=lambda x: x.confidence, reverse=True)
        
        # Sort web mentions by relevance
        person_data.web_mentions.sort(key=lambda x: x.relevance_score, reverse=True)
    
    def _extract_interests_from_text(self, text: str) -> List[str]:
        """Extract potential interests from text"""
        interests = []
        
        # Common interest keywords
        interest_keywords = [
            'love', 'passion', 'enjoy', 'hobby', 'interest', 'fan of',
            'music', 'sports', 'travel', 'photography', 'cooking', 'reading',
            'fitness', 'yoga', 'meditation', 'art', 'design', 'technology'
        ]
        
        text_lower = text.lower()
        for keyword in interest_keywords:
            if keyword in text_lower:
                interests.append(keyword)
        
        return interests
    
    def print_comprehensive_results(self, person_data: PersonData):
        """Print comprehensive search results"""
        print(f"\n👤 Comprehensive Profile for: {person_data.name}")
        print("=" * 80)
        print(f"🎯 Overall Confidence Score: {person_data.confidence_score:.1%}")
        
        if person_data.locations:
            print(f"📍 Locations: {', '.join(person_data.locations)}")
        
        # Social Media Profiles
        if person_data.profiles:
            print(f"\n📱 Social Media Profiles ({len(person_data.profiles)} found):")
            print("-" * 50)
            
            for profile in person_data.profiles[:10]:  # Show top 10
                verified_badge = "✓" if profile.verified else ""
                private_badge = "🔒" if profile.private else ""
                
                print(f"\n🔹 {profile.platform.title()}: @{profile.username} {verified_badge} {private_badge}")
                print(f"   Name: {profile.full_name}")
                print(f"   URL: {profile.url}")
                if profile.bio:
                    print(f"   Bio: {profile.bio[:100]}{'...' if len(profile.bio) > 100 else ''}")
                if profile.location:
                    print(f"   Location: {profile.location}")
                if profile.followers > 0:
                    print(f"   Followers: {profile.followers:,}")
                print(f"   Confidence: {profile.confidence:.1%}")
        
        # Professional Information
        if person_data.professional_info or any('work_history' in p.additional_info for p in person_data.profiles):
            print(f"\n💼 Professional Information:")
            print("-" * 50)
            
            # Work history from LinkedIn
            for profile in person_data.profiles:
                if profile.platform == 'linkedin' and 'work_history' in profile.additional_info:
                    print(f"\n🏢 Work History (from LinkedIn):")
                    for job in profile.additional_info['work_history'][:5]:
                        print(f"   • {job['title']} at {job['company']}")
                
                if profile.platform == 'linkedin' and 'education' in profile.additional_info:
                    print(f"\n🎓 Education (from LinkedIn):")
                    for edu in profile.additional_info['education'][:3]:
                        print(f"   • {edu['degree']} at {edu['school']}")
        
        # Skills and Interests
        if person_data.skills:
            print(f"\n🛠️  Skills ({len(person_data.skills)}):")
            print(f"   {', '.join(person_data.skills[:15])}")
        
        if person_data.interests:
            print(f"\n🎯 Interests ({len(person_data.interests)}):")
            print(f"   {', '.join(person_data.interests[:10])}")
        
        # Web Mentions
        if person_data.web_mentions:
            print(f"\n🌐 Web Mentions ({len(person_data.web_mentions)} found):")
            print("-" * 50)
            
            for mention in person_data.web_mentions[:10]:  # Show top 10
                print(f"\n🔗 {mention.mention_type.title()}: {mention.title}")
                print(f"   URL: {mention.url}")
                if mention.snippet:
                    print(f"   Snippet: {mention.snippet[:150]}{'...' if len(mention.snippet) > 150 else ''}")
                print(f"   Relevance: {mention.relevance_score:.1%}")
    
    def save_comprehensive_results(self, person_data: PersonData, filename: str = None):
        """Save comprehensive results to JSON file"""
        if filename is None:
            filename = f"comprehensive_search_{person_data.name.replace(' ', '_').lower()}.json"
        
        # Convert dataclasses to dictionaries
        data = {
            'name': person_data.name,
            'confidence_score': person_data.confidence_score,
            'locations': list(person_data.locations),
            'skills': person_data.skills,
            'interests': person_data.interests,
            'professional_info': person_data.professional_info,
            'contact_info': person_data.contact_info,
            'associations': person_data.associations,
            'education': person_data.education,
            'work_history': person_data.work_history,
            'profiles': [
                {
                    'platform': p.platform,
                    'username': p.username,
                    'full_name': p.full_name,
                    'bio': p.bio,
                    'location': p.location,
                    'followers': p.followers,
                    'following': p.following,
                    'posts': p.posts,
                    'verified': p.verified,
                    'private': p.private,
                    'url': p.url,
                    'profile_image': p.profile_image,
                    'additional_info': p.additional_info,
                    'confidence': p.confidence,
                    'last_updated': p.last_updated
                }
                for p in person_data.profiles
            ],
            'web_mentions': [
                {
                    'url': m.url,
                    'title': m.title,
                    'snippet': m.snippet,
                    'source': m.source,
                    'date': m.date,
                    'relevance_score': m.relevance_score,
                    'mention_type': m.mention_type
                }
                for m in person_data.web_mentions
            ],
            'timestamp': time.time()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Comprehensive results saved to: {filename}")

def main():
    finder = ComprehensivePersonFinder()
    
    print("🔍 Comprehensive Person Finder")
    print("=" * 60)
    print("Advanced search across multiple platforms:")
    print("• LinkedIn, Instagram, Twitter, Facebook")
    print("• Web mentions and articles")
    print("• Professional directories")
    print("• News and press mentions")
    print("=" * 60)
    
    while True:
        name = input("\nEnter person's name (or 'quit' to exit): ").strip()
        
        if name.lower() in ['quit', 'exit', 'q']:
            break
        
        if not name:
            print("Please enter a valid name")
            continue
        
        # Optional additional information
        location = input("Enter location (optional): ").strip() or None
        additional_info = input("Enter additional info (company, title, etc.) (optional): ").strip() or None
        
        print("\n🚀 Starting comprehensive search...")
        print("This may take 30-60 seconds...")
        
        # Perform comprehensive search
        start_time = time.time()
        person_data = finder.comprehensive_search(name, location, additional_info)
        end_time = time.time()
        
        print(f"\n⏱️  Search completed in {end_time - start_time:.1f} seconds")
        
        if person_data.profiles or person_data.web_mentions:
            # Print results
            finder.print_comprehensive_results(person_data)
            
            # Save results
            save = input("\nSave results to file? (y/n): ").lower()
            if save == 'y':
                finder.save_comprehensive_results(person_data)
        else:
            print("❌ No information found. Try with different search terms or additional info.")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    main() 