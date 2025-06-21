#!/usr/bin/env python3
"""
Advanced Social Media Scraper

Uses Selenium for robust web scraping of social media platforms.
This can handle JavaScript-heavy sites and dynamic content.
"""

import time
import json
import re
from typing import List, Dict
from dataclasses import dataclass
from urllib.parse import quote_plus
import os

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium not available. Install with: pip install selenium webdriver-manager")

@dataclass
class SocialProfile:
    platform: str
    username: str
    url: str
    display_name: str
    bio: str = ""
    followers: int = 0
    verified: bool = False
    private: bool = False
    confidence: float = 0.0
    profile_image: str = ""

class AdvancedSocialScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.setup_driver()
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        if not SELENIUM_AVAILABLE:
            print("Selenium not available. Using fallback methods.")
            return
            
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Try to use webdriver-manager for automatic chromedriver
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except:
                # Fallback to system chromedriver
                self.driver = webdriver.Chrome(options=chrome_options)
                
            print("✅ Chrome driver initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Chrome driver: {e}")
            print("Falling back to requests-based scraping")
            self.driver = None
    
    def search_instagram_selenium(self, name: str) -> List[SocialProfile]:
        """Search Instagram using Selenium"""
        profiles = []
        
        if not self.driver:
            return profiles
            
        try:
            # Go to Instagram search
            search_url = f"https://www.instagram.com/explore/tags/{quote_plus(name)}/"
            self.driver.get(search_url)
            time.sleep(3)
            
            # Look for user profiles in search results
            try:
                # Wait for content to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "a"))
                )
                
                # Find profile links
                links = self.driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    if href and "/p/" in href:
                        # This is a post, try to find the username
                        try:
                            username_element = link.find_element(By.XPATH, ".//span[contains(@class, '_aacl')]")
                            username = username_element.text
                            if username and username != name:
                                profile = SocialProfile(
                                    platform="Instagram",
                                    username=username,
                                    url=f"https://instagram.com/{username}",
                                    display_name=name,
                                    confidence=0.6
                                )
                                profiles.append(profile)
                        except:
                            continue
                            
            except TimeoutException:
                print("Timeout waiting for Instagram content to load")
                
        except Exception as e:
            print(f"Error searching Instagram with Selenium: {e}")
        
        return profiles[:5]  # Limit results
    
    def search_twitter_selenium(self, name: str) -> List[SocialProfile]:
        """Search Twitter using Selenium"""
        profiles = []
        
        if not self.driver:
            return profiles
            
        try:
            # Go to Twitter search
            search_url = f"https://twitter.com/search?q={quote_plus(name)}&src=typed_query&f=user"
            self.driver.get(search_url)
            time.sleep(5)
            
            try:
                # Wait for content to load
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "a"))
                )
                
                # Find user profile links
                links = self.driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    if href and "/status/" not in href and "/" in href:
                        # Extract username from URL
                        username = href.split("/")[-1]
                        if username and len(username) > 1 and not username.startswith("?"):
                            profile = SocialProfile(
                                platform="Twitter",
                                username=username,
                                url=href,
                                display_name=name,
                                confidence=0.7
                            )
                            profiles.append(profile)
                            
            except TimeoutException:
                print("Timeout waiting for Twitter content to load")
                
        except Exception as e:
            print(f"Error searching Twitter with Selenium: {e}")
        
        return profiles[:5]  # Limit results
    
    def search_linkedin_selenium(self, name: str) -> List[SocialProfile]:
        """Search LinkedIn using Selenium"""
        profiles = []
        
        if not self.driver:
            return profiles
            
        try:
            # Go to LinkedIn search
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={quote_plus(name)}"
            self.driver.get(search_url)
            time.sleep(5)
            
            try:
                # Wait for content to load
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "a"))
                )
                
                # Find profile links
                links = self.driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    if href and "/in/" in href:
                        # Extract username from LinkedIn URL
                        username = href.split("/in/")[-1].split("/")[0]
                        if username and len(username) > 1:
                            profile = SocialProfile(
                                platform="LinkedIn",
                                username=username,
                                url=href,
                                display_name=name,
                                confidence=0.8
                            )
                            profiles.append(profile)
                            
            except TimeoutException:
                print("Timeout waiting for LinkedIn content to load")
                
        except Exception as e:
            print(f"Error searching LinkedIn with Selenium: {e}")
        
        return profiles[:5]  # Limit results
    
    def search_github_api(self, name: str) -> List[SocialProfile]:
        """Search GitHub using their API (no Selenium needed)"""
        import requests
        
        profiles = []
        
        try:
            # Generate username variations
            usernames = self._generate_username_variations(name)
            
            for username in usernames[:5]:
                try:
                    url = f"https://api.github.com/users/{username}"
                    headers = {
                        'Accept': 'application/vnd.github.v3+json',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    }
                    
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        user_data = response.json()
                        
                        profile = SocialProfile(
                            platform="GitHub",
                            username=user_data.get('login', username),
                            url=user_data.get('html_url', f"https://github.com/{username}"),
                            display_name=user_data.get('name', name),
                            bio=user_data.get('bio', ''),
                            followers=user_data.get('followers', 0),
                            verified=False,
                            private=False,
                            confidence=0.9,
                            profile_image=user_data.get('avatar_url', '')
                        )
                        profiles.append(profile)
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    print(f"Error searching GitHub for '{username}': {e}")
                    continue
            
            return profiles
            
        except Exception as e:
            print(f"Error in GitHub search: {e}")
            return []
    
    def _generate_username_variations(self, name: str) -> List[str]:
        """Generate username variations"""
        variations = []
        
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
        name_parts = clean_name.split()
        
        # Basic variations
        variations.extend([
            clean_name,
            clean_name.replace(' ', ''),
            clean_name.replace(' ', '_'),
            clean_name.replace(' ', '.'),
        ])
        
        # First and last name combinations
        if len(name_parts) >= 2:
            first, last = name_parts[0], name_parts[-1]
            variations.extend([
                f"{first}{last}",
                f"{first}_{last}",
                f"{first}.{last}",
                f"{first[0]}{last}",
            ])
        
        return list(set(variations))
    
    def search_all_platforms(self, name: str) -> Dict[str, List[SocialProfile]]:
        """Search for profiles across all platforms"""
        print(f"🔍 Advanced searching for: {name}")
        print("This may take a few moments...")
        
        results = {
            'instagram': self.search_instagram_selenium(name),
            'twitter': self.search_twitter_selenium(name),
            'linkedin': self.search_linkedin_selenium(name),
            'github': self.search_github_api(name),
        }
        
        return results
    
    def print_results(self, results: Dict[str, List[SocialProfile]]):
        """Print search results"""
        print("\n" + "="*60)
        print("ADVANCED SOCIAL MEDIA SEARCH RESULTS")
        print("="*60)
        
        total_profiles = 0
        
        for platform, profiles in results.items():
            if profiles:
                total_profiles += len(profiles)
                print(f"\n📱 {platform.upper()}:")
                print("-" * 40)
                
                for i, profile in enumerate(profiles, 1):
                    verified_badge = "✓" if profile.verified else ""
                    private_badge = "🔒" if profile.private else ""
                    
                    print(f"  {i}. @{profile.username} {verified_badge} {private_badge}")
                    print(f"     Name: {profile.display_name}")
                    print(f"     URL: {profile.url}")
                    if profile.bio:
                        print(f"     Bio: {profile.bio[:100]}{'...' if len(profile.bio) > 100 else ''}")
                    if profile.followers > 0:
                        print(f"     Followers: {profile.followers:,}")
                    print(f"     Confidence: {profile.confidence:.1%}")
                    print()
        
        print(f"📊 Total: {total_profiles} real profiles found")
    
    def save_results(self, name: str, results: Dict[str, List[SocialProfile]], filename: str = None):
        """Save results to JSON file"""
        if filename is None:
            filename = f"advanced_social_results_{name.replace(' ', '_').lower()}.json"
        
        data = {
            'search_name': name,
            'timestamp': time.time(),
            'results': {}
        }
        
        for platform, profiles in results.items():
            data['results'][platform] = [
                {
                    'platform': p.platform,
                    'username': p.username,
                    'url': p.url,
                    'display_name': p.display_name,
                    'bio': p.bio,
                    'followers': p.followers,
                    'verified': p.verified,
                    'private': p.private,
                    'confidence': p.confidence,
                    'profile_image': p.profile_image
                }
                for p in profiles
            ]
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Results saved to: {filename}")
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()

def main():
    scraper = AdvancedSocialScraper(headless=True)
    
    print("🔍 Advanced Social Media Profile Scraper")
    print("=" * 50)
    print("Uses Selenium for robust web scraping")
    print("to find real social media profiles!")
    print("=" * 50)
    
    try:
        while True:
            name = input("\nEnter person's name (or 'quit' to exit): ").strip()
            
            if name.lower() in ['quit', 'exit', 'q']:
                break
            
            if not name:
                print("Please enter a valid name")
                continue
            
            # Search all platforms
            results = scraper.search_all_platforms(name)
            
            # Print results
            scraper.print_results(results)
            
            # Save results
            save = input("\nSave results to file? (y/n): ").lower()
            if save == 'y':
                scraper.save_results(name, results)
            
            print("\n" + "-" * 50)
    
    finally:
        scraper.close()

if __name__ == "__main__":
    main() 