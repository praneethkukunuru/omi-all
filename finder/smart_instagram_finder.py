#!/usr/bin/env python3
"""
Smart Instagram Profile Finder

Uses multiple search strategies to find Instagram profiles even when
usernames don't match the person's real name.
"""

import requests
import json
import time
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from urllib.parse import quote_plus
import os

@dataclass
class InstagramProfile:
    username: str
    full_name: str
    bio: str
    followers: int
    following: int
    posts: int
    verified: bool
    private: bool
    url: str
    profile_image: str
    search_method: str
    confidence: float

class SmartInstagramFinder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
        
        # Instagram endpoints
        self.search_url = "https://www.instagram.com/web/search/topsearch/"
        self.profile_url = "https://www.instagram.com/{username}/"
        self.hashtag_url = "https://www.instagram.com/explore/tags/{hashtag}/"
        
    def search_by_name_variations(self, name: str) -> List[InstagramProfile]:
        """Search using various name combinations"""
        profiles = []
        
        # Generate name variations
        name_variations = self._generate_name_variations(name)
        
        for variation in name_variations[:8]:  # Try more variations
            try:
                print(f"    Trying: {variation}")
                
                # Method 1: Try the search API
                profiles.extend(self._search_api(variation, f"Name variation: {variation}"))
                
                # Method 2: Try direct profile access
                profile = self._check_profile_exists(variation, f"Direct profile: {variation}")
                if profile:
                    profiles.append(profile)
                
                time.sleep(1)  # Shorter delay
                
            except Exception as e:
                print(f"    Error with '{variation}': {e}")
                continue
        
        return profiles
    
    def _search_api(self, query: str, method: str) -> List[InstagramProfile]:
        """Search using Instagram's API"""
        profiles = []
        
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
                'X-IG-WWW-Claim': '0',
            })
            
            response = self.session.get(self.search_url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    users = data.get('users', [])
                    
                    for user_data in users[:3]:
                        user = user_data.get('user', {})
                        if user and user.get('username'):
                            profile = InstagramProfile(
                                username=user.get('username', ''),
                                full_name=user.get('full_name', ''),
                                bio=user.get('biography', ''),
                                followers=user.get('follower_count', 0),
                                following=user.get('following_count', 0),
                                posts=user.get('media_count', 0),
                                verified=user.get('is_verified', False),
                                private=user.get('is_private', False),
                                url=f"https://instagram.com/{user.get('username', '')}",
                                profile_image=user.get('profile_pic_url', ''),
                                search_method=method,
                                confidence=0.7
                            )
                            profiles.append(profile)
                except json.JSONDecodeError:
                    print(f"    JSON decode error for {query}")
                    
        except Exception as e:
            print(f"    API search failed for {query}: {e}")
        
        return profiles
    
    def _check_profile_exists(self, username: str, method: str) -> Optional[InstagramProfile]:
        """Check if a profile exists by accessing it directly"""
        try:
            url = self.profile_url.format(username=username)
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                # Check if it's a valid profile page (not a 404 or error page)
                if 'profile' in response.text.lower() or 'instagram' in response.text.lower():
                    # Try to extract basic info from the page
                    return InstagramProfile(
                        username=username,
                        full_name=username,  # We don't have the full name yet
                        bio="",
                        followers=0,
                        following=0,
                        posts=0,
                        verified=False,
                        private=False,
                        url=url,
                        profile_image="",
                        search_method=method,
                        confidence=0.5
                    )
            
        except Exception as e:
            print(f"    Profile check failed for {username}: {e}")
        
        return None
    
    def search_by_hashtags(self, name: str) -> List[InstagramProfile]:
        """Search for profiles using hashtags related to the name"""
        profiles = []
        
        # Generate hashtag variations
        hashtags = self._generate_hashtags(name)
        
        for hashtag in hashtags[:5]:
            try:
                print(f"    Trying hashtag: #{hashtag}")
                
                # Search for posts with this hashtag
                profiles.extend(self._search_api(f"#{hashtag}", f"Hashtag: #{hashtag}"))
                
                time.sleep(1)
                
            except Exception as e:
                print(f"    Error searching hashtag #{hashtag}: {e}")
                continue
        
        return profiles
    
    def search_by_bio_keywords(self, name: str) -> List[InstagramProfile]:
        """Search for profiles that mention the name in their bio"""
        profiles = []
        
        # Generate bio search keywords
        keywords = self._generate_bio_keywords(name)
        
        for keyword in keywords[:5]:
            try:
                print(f"    Trying bio keyword: {keyword}")
                
                profiles.extend(self._search_api(keyword, f"Bio keyword: {keyword}"))
                
                time.sleep(1)
                
            except Exception as e:
                print(f"    Error searching bio keyword '{keyword}': {e}")
                continue
        
        return profiles
    
    def search_by_location(self, name: str, location: str = None) -> List[InstagramProfile]:
        """Search for profiles by location if provided"""
        profiles = []
        
        if not location:
            return profiles
        
        try:
            print(f"    Trying location: {location}")
            
            profiles.extend(self._search_api(location, f"Location: {location}"))
            
            time.sleep(1)
            
        except Exception as e:
            print(f"    Error searching by location '{location}': {e}")
        
        return profiles
    
    def search_by_common_usernames(self, name: str) -> List[InstagramProfile]:
        """Search for common username patterns"""
        profiles = []
        
        # Generate common username patterns
        usernames = self._generate_common_usernames(name)
        
        for username in usernames[:10]:
            try:
                print(f"    Trying common username: {username}")
                
                profile = self._check_profile_exists(username, f"Common pattern: {username}")
                if profile:
                    profiles.append(profile)
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    Error with username {username}: {e}")
                continue
        
        return profiles
    
    def _generate_name_variations(self, name: str) -> List[str]:
        """Generate various name combinations"""
        variations = []
        
        # Clean the name
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        name_parts = clean_name.split()
        
        # Basic variations
        variations.extend([
            clean_name,
            clean_name.replace(' ', ''),
            clean_name.replace(' ', '_'),
            clean_name.replace(' ', '.'),
            clean_name.replace(' ', ''),
        ])
        
        # First and last name combinations
        if len(name_parts) >= 2:
            first, last = name_parts[0], name_parts[-1]
            variations.extend([
                f"{first} {last}",
                f"{first}{last}",
                f"{first}_{last}",
                f"{first}.{last}",
                f"{first[0]}{last}",
                f"{first}{last[0]}",
                f"{first[0]}.{last}",
                f"{first}.{last[0]}",
                f"{first}{last}1",
                f"{first}{last}2",
                f"{first}{last}3",
            ])
        
        # Add common prefixes/suffixes
        if len(name_parts) >= 2:
            first, last = name_parts[0], name_parts[-1]
            variations.extend([
                f"the{first}{last}",
                f"real{first}{last}",
                f"{first}{last}official",
                f"{first}{last}real",
                f"{first}{last}official",
                f"{first}{last}official",
            ])
        
        return list(set(variations))
    
    def _generate_common_usernames(self, name: str) -> List[str]:
        """Generate common username patterns"""
        usernames = []
        
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
        name_parts = clean_name.split()
        
        if len(name_parts) >= 2:
            first, last = name_parts[0], name_parts[-1]
            
            # Common patterns
            usernames.extend([
                f"{first}{last}",
                f"{first}_{last}",
                f"{first}.{last}",
                f"{first[0]}{last}",
                f"{first}{last[0]}",
                f"{first[0]}.{last}",
                f"{first}.{last[0]}",
                f"{first}{last}1",
                f"{first}{last}2",
                f"{first}{last}3",
                f"{first}{last}official",
                f"{first}{last}real",
                f"real{first}{last}",
                f"the{first}{last}",
            ])
        
        return list(set(usernames))
    
    def _generate_hashtags(self, name: str) -> List[str]:
        """Generate hashtag variations"""
        hashtags = []
        
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', name.lower())
        name_parts = clean_name.split()
        
        # Basic hashtags
        hashtags.extend([
            clean_name.replace(' ', ''),
            clean_name.replace(' ', ''),
        ])
        
        # First and last name hashtags
        if len(name_parts) >= 2:
            first, last = name_parts[0], name_parts[-1]
            hashtags.extend([
                f"{first}{last}",
                f"{first}_{last}",
                f"{first}{last}official",
                f"{first}{last}real",
            ])
        
        return list(set(hashtags))
    
    def _generate_bio_keywords(self, name: str) -> List[str]:
        """Generate keywords to search in bios"""
        keywords = []
        
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        name_parts = clean_name.split()
        
        # Basic keywords
        keywords.extend([
            clean_name,
            clean_name.replace(' ', ''),
        ])
        
        # First and last name keywords
        if len(name_parts) >= 2:
            first, last = name_parts[0], name_parts[-1]
            keywords.extend([
                f"{first} {last}",
                f"{first}{last}",
                f"{first} {last[0]}",  # First name + last initial
            ])
        
        return list(set(keywords))
    
    def smart_search(self, name: str, location: str = None) -> List[InstagramProfile]:
        """Perform comprehensive smart search"""
        print(f"🔍 Smart Instagram search for: {name}")
        print("Using multiple search strategies...")
        
        all_profiles = []
        
        # Strategy 1: Name variations
        print("  📝 Searching name variations...")
        profiles = self.search_by_name_variations(name)
        all_profiles.extend(profiles)
        
        # Strategy 2: Common username patterns
        print("  🎯 Searching common username patterns...")
        profiles = self.search_by_common_usernames(name)
        all_profiles.extend(profiles)
        
        # Strategy 3: Hashtag search
        print("  #️⃣ Searching hashtags...")
        profiles = self.search_by_hashtags(name)
        all_profiles.extend(profiles)
        
        # Strategy 4: Bio keyword search
        print("  📖 Searching bio keywords...")
        profiles = self.search_by_bio_keywords(name)
        all_profiles.extend(profiles)
        
        # Strategy 5: Location search (if provided)
        if location:
            print(f"  📍 Searching by location: {location}")
            profiles = self.search_by_location(name, location)
            all_profiles.extend(profiles)
        
        # Remove duplicates and sort by confidence
        unique_profiles = self._remove_duplicates(all_profiles)
        unique_profiles.sort(key=lambda x: x.confidence, reverse=True)
        
        return unique_profiles
    
    def _remove_duplicates(self, profiles: List[InstagramProfile]) -> List[InstagramProfile]:
        """Remove duplicate profiles based on username"""
        seen_usernames = set()
        unique_profiles = []
        
        for profile in profiles:
            if profile.username and profile.username not in seen_usernames:
                seen_usernames.add(profile.username)
                unique_profiles.append(profile)
        
        return unique_profiles
    
    def print_results(self, profiles: List[InstagramProfile]):
        """Print search results"""
        print(f"\n📸 Found {len(profiles)} Instagram profiles:")
        print("=" * 60)
        
        for i, profile in enumerate(profiles, 1):
            verified_badge = "✓" if profile.verified else ""
            private_badge = "🔒" if profile.private else ""
            
            print(f"\n{i}. @{profile.username} {verified_badge} {private_badge}")
            print(f"   Name: {profile.full_name}")
            print(f"   URL: {profile.url}")
            if profile.bio:
                print(f"   Bio: {profile.bio[:100]}{'...' if len(profile.bio) > 100 else ''}")
            if profile.followers > 0:
                print(f"   Followers: {profile.followers:,}")
            if profile.following > 0:
                print(f"   Following: {profile.following:,}")
            if profile.posts > 0:
                print(f"   Posts: {profile.posts:,}")
            print(f"   Found via: {profile.search_method}")
            print(f"   Confidence: {profile.confidence:.1%}")
    
    def save_results(self, name: str, profiles: List[InstagramProfile], filename: str = None):
        """Save results to JSON file"""
        if filename is None:
            filename = f"smart_instagram_results_{name.replace(' ', '_').lower()}.json"
        
        data = {
            'search_name': name,
            'timestamp': time.time(),
            'total_profiles': len(profiles),
            'profiles': [
                {
                    'username': p.username,
                    'full_name': p.full_name,
                    'bio': p.bio,
                    'followers': p.followers,
                    'following': p.following,
                    'posts': p.posts,
                    'verified': p.verified,
                    'private': p.private,
                    'url': p.url,
                    'profile_image': p.profile_image,
                    'search_method': p.search_method,
                    'confidence': p.confidence
                }
                for p in profiles
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Results saved to: {filename}")

def main():
    finder = SmartInstagramFinder()
    
    print("🔍 Smart Instagram Profile Finder")
    print("=" * 50)
    print("Uses multiple strategies to find profiles")
    print("even when usernames don't match real names!")
    print("=" * 50)
    
    while True:
        name = input("\nEnter person's name (or 'quit' to exit): ").strip()
        
        if name.lower() in ['quit', 'exit', 'q']:
            break
        
        if not name:
            print("Please enter a valid name")
            continue
        
        location = input("Enter location (optional, press Enter to skip): ").strip()
        if not location:
            location = None
        
        # Perform smart search
        profiles = finder.smart_search(name, location)
        
        if profiles:
            # Print results
            finder.print_results(profiles)
            
            # Save results
            save = input("\nSave results to file? (y/n): ").lower()
            if save == 'y':
                finder.save_results(name, profiles)
        else:
            print("No profiles found.")
        
        print("\n" + "-" * 50)

if __name__ == "__main__":
    main() 