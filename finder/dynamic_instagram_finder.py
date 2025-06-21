#!/usr/bin/env python3
"""
Dynamic Instagram Profile Finder

Takes initial search results and builds off them to find more profiles,
rather than being limited to specific patterns.
"""

import requests
import json
import time
import re
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from urllib.parse import quote_plus, urlparse
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

class DynamicInstagramFinder:
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
        self.followers_url = "https://www.instagram.com/{username}/followers/"
        self.following_url = "https://www.instagram.com/{username}/following/"
        
    def get_initial_results(self, name: str) -> List[InstagramProfile]:
        """Get first 5 search results for the name"""
        print(f"🔍 Getting initial results for: {name}")
        
        profiles = []
        
        # Try different search queries
        search_queries = [
            name,
            name.replace(' ', ''),
            name.replace(' ', '_'),
            name.replace(' ', '.'),
        ]
        
        for query in search_queries[:3]:
            try:
                print(f"  Trying query: {query}")
                
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
                        
                        for user_data in users[:5]:  # Get first 5 results
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
                                    search_method=f"Initial search: {query}",
                                    confidence=0.8
                                )
                                profiles.append(profile)
                                
                    except json.JSONDecodeError:
                        print(f"    JSON decode error for {query}")
                        
            except Exception as e:
                print(f"    Error with query '{query}': {e}")
                continue
            
            time.sleep(1)
        
        return profiles[:5]  # Return only first 5
    
    def expand_from_profile(self, profile: InstagramProfile) -> List[InstagramProfile]:
        """Expand search from a single profile"""
        print(f"  🔗 Expanding from @{profile.username}")
        
        new_profiles = []
        
        # Method 1: Extract usernames from bio
        bio_usernames = self._extract_usernames_from_bio(profile.bio)
        for username in bio_usernames[:3]:
            new_profile = self._get_profile_info(username, f"Bio mention from @{profile.username}")
            if new_profile:
                new_profiles.append(new_profile)
        
        # Method 2: Extract usernames from full name
        name_usernames = self._extract_usernames_from_name(profile.full_name)
        for username in name_usernames[:3]:
            new_profile = self._get_profile_info(username, f"Name variation from @{profile.username}")
            if new_profile:
                new_profiles.append(new_profile)
        
        # Method 3: Try similar usernames
        similar_usernames = self._generate_similar_usernames(profile.username)
        for username in similar_usernames[:3]:
            new_profile = self._get_profile_info(username, f"Similar to @{profile.username}")
            if new_profile:
                new_profiles.append(new_profile)
        
        return new_profiles
    
    def expand_from_all_profiles(self, initial_profiles: List[InstagramProfile]) -> List[InstagramProfile]:
        """Expand search from all initial profiles"""
        print("🔄 Expanding search from initial results...")
        
        all_profiles = initial_profiles.copy()
        expanded_profiles = []
        
        for profile in initial_profiles:
            print(f"  📍 Expanding from @{profile.username}")
            
            # Expand from this profile
            new_profiles = self.expand_from_profile(profile)
            
            # Add new profiles that we haven't seen before
            for new_profile in new_profiles:
                if not any(p.username == new_profile.username for p in all_profiles + expanded_profiles):
                    expanded_profiles.append(new_profile)
            
            time.sleep(1)
        
        return expanded_profiles
    
    def _extract_usernames_from_bio(self, bio: str) -> List[str]:
        """Extract usernames mentioned in bio"""
        usernames = []
        
        if not bio:
            return usernames
        
        # Look for @username patterns
        mentions = re.findall(r'@(\w+)', bio)
        usernames.extend(mentions)
        
        # Look for "username" patterns
        quoted = re.findall(r'"(\w+)"', bio)
        usernames.extend(quoted)
        
        # Look for common patterns like "DM me at username"
        dm_patterns = re.findall(r'DM.*?(\w+)', bio, re.IGNORECASE)
        usernames.extend(dm_patterns)
        
        return list(set(usernames))
    
    def _extract_usernames_from_name(self, full_name: str) -> List[str]:
        """Extract possible usernames from full name"""
        usernames = []
        
        if not full_name:
            return usernames
        
        # Clean the name
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', full_name)
        name_parts = clean_name.split()
        
        if len(name_parts) >= 2:
            first, last = name_parts[0], name_parts[-1]
            
            # Generate variations
            usernames.extend([
                f"{first}{last}",
                f"{first}_{last}",
                f"{first}.{last}",
                f"{first[0]}{last}",
                f"{first}{last[0]}",
                f"{first[0]}.{last}",
                f"{first}.{last[0]}",
            ])
        
        return list(set(usernames))
    
    def _generate_similar_usernames(self, username: str) -> List[str]:
        """Generate usernames similar to the given one"""
        similar = []
        
        # Add numbers
        for i in range(1, 4):
            similar.append(f"{username}{i}")
            similar.append(f"{username}_{i}")
            similar.append(f"{username}.{i}")
        
        # Add common suffixes
        suffixes = ['official', 'real', 'official', 'official', 'official']
        for suffix in suffixes:
            similar.append(f"{username}{suffix}")
            similar.append(f"{username}_{suffix}")
        
        # Add common prefixes
        prefixes = ['the', 'real', 'official']
        for prefix in prefixes:
            similar.append(f"{prefix}{username}")
            similar.append(f"{prefix}_{username}")
        
        return list(set(similar))
    
    def _get_profile_info(self, username: str, method: str) -> Optional[InstagramProfile]:
        """Get profile information for a username"""
        try:
            # Try to get profile via API first
            profile = self._get_profile_via_api(username, method)
            if profile:
                return profile
            
            # Fallback: check if profile exists
            profile = self._check_profile_exists(username, method)
            return profile
            
        except Exception as e:
            print(f"    Error getting profile for {username}: {e}")
            return None
    
    def _get_profile_via_api(self, username: str, method: str) -> Optional[InstagramProfile]:
        """Get profile via Instagram API"""
        try:
            params = {
                'query': username,
                'context': 'blended'
            }
            
            headers = self.session.headers.copy()
            headers.update({
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://www.instagram.com/',
                'X-IG-App-ID': '936619743392459',
                'X-IG-WWW-Claim': '0',
            })
            
            response = self.session.get(self.search_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                
                for user_data in users:
                    user = user_data.get('user', {})
                    if user and user.get('username') == username:
                        return InstagramProfile(
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
            
        except Exception as e:
            print(f"    API error for {username}: {e}")
        
        return None
    
    def _check_profile_exists(self, username: str, method: str) -> Optional[InstagramProfile]:
        """Check if profile exists by accessing it directly"""
        try:
            url = self.profile_url.format(username=username)
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                # Check if it's a valid profile page
                if 'profile' in response.text.lower() or 'instagram' in response.text.lower():
                    return InstagramProfile(
                        username=username,
                        full_name=username,
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
            print(f"    Profile check error for {username}: {e}")
        
        return None
    
    def dynamic_search(self, name: str) -> List[InstagramProfile]:
        """Perform dynamic search that builds off initial results"""
        print(f"🔍 Dynamic Instagram search for: {name}")
        print("=" * 50)
        
        # Step 1: Get initial results
        initial_profiles = self.get_initial_results(name)
        
        if not initial_profiles:
            print("❌ No initial results found. Trying alternative methods...")
            # Fallback: try some common patterns
            fallback_profiles = self._fallback_search(name)
            return fallback_profiles
        
        print(f"✅ Found {len(initial_profiles)} initial profiles")
        
        # Step 2: Expand from initial results
        expanded_profiles = self.expand_from_all_profiles(initial_profiles)
        
        print(f"✅ Found {len(expanded_profiles)} additional profiles")
        
        # Step 3: Combine and remove duplicates
        all_profiles = initial_profiles + expanded_profiles
        unique_profiles = self._remove_duplicates(all_profiles)
        
        # Step 4: Sort by relevance
        unique_profiles.sort(key=lambda x: x.confidence, reverse=True)
        
        return unique_profiles
    
    def _fallback_search(self, name: str) -> List[InstagramProfile]:
        """Fallback search when initial search fails"""
        print("🔄 Using fallback search methods...")
        
        profiles = []
        
        # Try some common username patterns
        common_patterns = self._generate_common_patterns(name)
        
        for pattern in common_patterns[:10]:
            try:
                print(f"  Trying fallback pattern: {pattern}")
                profile = self._check_profile_exists(pattern, f"Fallback: {pattern}")
                if profile:
                    profiles.append(profile)
                time.sleep(0.5)
            except Exception as e:
                print(f"    Error with fallback pattern {pattern}: {e}")
                continue
        
        return profiles
    
    def _generate_common_patterns(self, name: str) -> List[str]:
        """Generate common username patterns for fallback"""
        patterns = []
        
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
        name_parts = clean_name.split()
        
        if len(name_parts) >= 2:
            first, last = name_parts[0], name_parts[-1]
            
            patterns.extend([
                f"{first}{last}",
                f"{first}_{last}",
                f"{first}.{last}",
                f"{first[0]}{last}",
                f"{first}{last[0]}",
                f"{first}{last}1",
                f"{first}{last}2",
                f"{first}{last}official",
                f"real{first}{last}",
                f"the{first}{last}",
            ])
        
        return patterns
    
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
            filename = f"dynamic_instagram_results_{name.replace(' ', '_').lower()}.json"
        
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
    finder = DynamicInstagramFinder()
    
    print("🔍 Dynamic Instagram Profile Finder")
    print("=" * 50)
    print("Gets initial results and builds off them")
    print("to find more related profiles!")
    print("=" * 50)
    
    while True:
        name = input("\nEnter person's name (or 'quit' to exit): ").strip()
        
        if name.lower() in ['quit', 'exit', 'q']:
            break
        
        if not name:
            print("Please enter a valid name")
            continue
        
        # Perform dynamic search
        profiles = finder.dynamic_search(name)
        
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