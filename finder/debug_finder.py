#!/usr/bin/env python3
"""
Debug Person Finder

Simple debug version to test what's happening with searches
"""

import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

def test_google_search(name):
    print(f"🔍 Testing Google search for: {name}")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    # Test simple Google search
    query = f'"{name}" Instagram OR LinkedIn OR Twitter'
    search_url = f"https://www.google.com/search?q={quote_plus(query)}"
    
    print(f"📡 URL: {search_url}")
    
    try:
        response = session.get(search_url, timeout=15)
        print(f"🔗 Status Code: {response.status_code}")
        print(f"📄 Response Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check if we got blocked
            if 'unusual traffic' in response.text.lower():
                print("⚠️  Blocked by Google (unusual traffic)")
            
            # Look for search results
            results = soup.find_all('div', class_='g')
            print(f"📊 Found {len(results)} search result containers")
            
            # Extract first few results
            for i, result in enumerate(results[:3]):
                link = result.find('a')
                title = result.find('h3')
                
                if link and title:
                    url = link.get('href', '')
                    title_text = title.get_text().strip()
                    
                    print(f"\n{i+1}. {title_text}")
                    print(f"   URL: {url}")
                    
                    # Check if it's a social media profile
                    if any(site in url.lower() for site in ['instagram', 'linkedin', 'twitter', 'facebook']):
                        print(f"   ✅ Social media profile detected!")
            
            if len(results) == 0:
                print("❌ No search results found")
                # Print first 500 chars of response to debug
                print(f"📄 Response preview: {response.text[:500]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_direct_instagram(username):
    print(f"\n🔍 Testing direct Instagram access for: {username}")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    url = f"https://www.instagram.com/{username}/"
    print(f"📡 URL: {url}")
    
    try:
        response = session.get(url, timeout=10)
        print(f"🔗 Status Code: {response.status_code}")
        print(f"📄 Response Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # Check if it's a valid profile
            content = response.text.lower()
            
            if 'followers' in content or 'following' in content:
                print("✅ Valid Instagram profile detected!")
                
                # Try to extract name from title
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.find('title')
                if title:
                    print(f"📝 Title: {title.get_text()}")
                
                # Try to extract from meta tags
                meta_desc = soup.find('meta', property='og:description')
                if meta_desc:
                    print(f"📝 Description: {meta_desc.get('content', '')}")
                    
            else:
                print("❌ Not a valid profile page")
        elif response.status_code == 404:
            print("❌ Profile not found")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_linkedin_direct(username):
    print(f"\n🔍 Testing direct LinkedIn access for: {username}")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    url = f"https://www.linkedin.com/in/{username}/"
    print(f"📡 URL: {url}")
    
    try:
        response = session.get(url, timeout=10)
        print(f"🔗 Status Code: {response.status_code}")
        print(f"📄 Response Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            content = response.text.lower()
            
            if 'linkedin' in content and ('profile' in content or 'experience' in content):
                print("✅ Valid LinkedIn profile detected!")
                
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.find('title')
                if title:
                    print(f"📝 Title: {title.get_text()}")
            else:
                print("❌ Not a valid LinkedIn profile")
                
                # Check if we need to log in
                if 'sign in' in content or 'login' in content:
                    print("⚠️  LinkedIn requires authentication")
                    
        elif response.status_code == 404:
            print("❌ Profile not found")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def generate_test_usernames(name):
    """Generate test usernames"""
    clean_name = name.lower().replace(' ', '')
    parts = name.lower().split()
    
    usernames = [clean_name]
    
    if len(parts) >= 2:
        first, last = parts[0], parts[-1]
        usernames.extend([
            f"{first}{last}",
            f"{first}_{last}",
            f"{first}.{last}",
            f"{first}{last}1"
        ])
    
    return usernames[:5]  # Return top 5

def main():
    print("🔧 Debug Person Finder")
    print("=" * 50)
    
    name = input("Enter a name to test: ").strip()
    
    if not name:
        print("Please enter a valid name")
        return
    
    # Test 1: Google search
    test_google_search(name)
    
    # Test 2: Direct profile access
    print("\n" + "=" * 50)
    print("Testing direct profile access...")
    
    usernames = generate_test_usernames(name)
    print(f"Generated usernames: {usernames}")
    
    # Test Instagram
    for username in usernames[:2]:  # Test first 2 usernames
        test_direct_instagram(username)
        time.sleep(1)
    
    # Test LinkedIn
    for username in usernames[:2]:
        test_linkedin_direct(username)
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("🔍 Debug complete!")
    print("\nTips for better results:")
    print("• Try common username variations")
    print("• Check if the person uses their real name as username")
    print("• Try with location or profession context")

if __name__ == "__main__":
    main() 