# Real Social Media Scraper

A comprehensive social media profile finder that **actually searches online platforms** using web scraping and API requests to find real profiles.

## 🎯 What It Does

This tool **really searches** social media platforms online to find actual profiles, not just generate possible usernames. It uses:

- **Web Scraping**: Real HTTP requests to platform search pages
- **API Integration**: Direct API calls to platforms like GitHub
- **Selenium**: Browser automation for JavaScript-heavy sites
- **Profile Validation**: Checks if profiles actually exist

## 🚀 Two Scraping Options

### 1. **Real Social Scraper** (`real_social_scraper.py`)
- Uses `requests` library for web scraping
- Searches Instagram, Twitter, GitHub, LinkedIn, Facebook
- Real API calls and web requests
- No browser needed
- **Recommended for most users**

### 2. **Advanced Scraper** (`advanced_scraper.py`)
- Uses **Selenium** for robust scraping
- Handles JavaScript-heavy sites
- Can bypass some anti-bot measures
- Requires Chrome browser
- **Use when basic scraper doesn't work**

## 📱 Supported Platforms

| Platform | Method | Real Search |
|----------|--------|-------------|
| Instagram | API + Web Scraping | ✅ Yes |
| Twitter | Web Scraping | ✅ Yes |
| GitHub | API | ✅ Yes |
| LinkedIn | Web Scraping | ✅ Yes |
| Facebook | Web Scraping | ✅ Yes |

## 🛠️ Installation

### Basic Setup (Real Scraper)
```bash
cd finder
pip install -r requirements.txt
```

### Advanced Setup (Selenium)
```bash
pip install selenium webdriver-manager
```

## 🎮 Usage

### Real Web Scraping (Recommended)
```bash
python real_social_scraper.py
```

### Advanced Selenium Scraping
```bash
python advanced_scraper.py
```

## 🔍 How Real Scraping Works

### Instagram Search
1. **API Call**: Uses Instagram's search API
2. **Query Generation**: Creates search queries from name
3. **Profile Extraction**: Gets real profile data
4. **Data Parsing**: Extracts username, bio, followers

### GitHub Search
1. **API Request**: Direct GitHub API calls
2. **Username Testing**: Tests generated usernames
3. **Profile Validation**: Confirms profiles exist
4. **Data Extraction**: Gets real user data

### LinkedIn Search
1. **Web Scraping**: Searches LinkedIn people search
2. **HTML Parsing**: Extracts profile links
3. **URL Extraction**: Finds real profile URLs
4. **Data Collection**: Gathers profile information

## 📊 Example Real Results

```
🔍 Real-time searching for: John Doe
This may take a few moments...

============================================================
REAL SOCIAL MEDIA SEARCH RESULTS
============================================================

📱 INSTAGRAM:
----------------------------------------
  1. @johndoe ✓
     Name: John Doe
     URL: https://instagram.com/johndoe
     Bio: Software developer and coffee enthusiast
     Followers: 1,234
     Confidence: 80%

📱 GITHUB:
----------------------------------------
  1. @johndoe
     Name: John Doe
     URL: https://github.com/johndoe
     Bio: Full-stack developer | Python enthusiast
     Followers: 567
     Confidence: 90%

📊 Total: 8 real profiles found
```

## ⚡ Performance

- **Real Scraper**: 10-30 seconds per search
- **Advanced Scraper**: 30-60 seconds per search
- **Rate Limiting**: Built-in delays to avoid blocking
- **Error Handling**: Graceful fallbacks for failed requests

## 🛡️ Anti-Detection Features

- **User-Agent Rotation**: Realistic browser headers
- **Request Delays**: Prevents rate limiting
- **Session Management**: Maintains cookies and state
- **Error Recovery**: Handles blocked requests gracefully

## 📁 File Structure

```
finder/
├── real_social_scraper.py     # Real web scraping with requests
├── advanced_scraper.py        # Selenium-based scraping
├── requirements.txt           # Dependencies
└── README.md                 # This file
```

## 🔧 Technical Details

### Real Scraper Features
- **HTTP Requests**: Direct platform API calls
- **JSON Parsing**: Extracts structured data
- **Regex Extraction**: Finds profile links in HTML
- **Error Handling**: Robust error recovery

### Advanced Scraper Features
- **Browser Automation**: Full browser control
- **JavaScript Support**: Handles dynamic content
- **Element Selection**: Precise data extraction
- **Headless Mode**: Runs without visible browser

## ⚠️ Important Notes

### Rate Limiting
- Instagram: 2-second delays between requests
- GitHub: 1-second delays (API rate limits)
- LinkedIn: 5-second delays for web scraping
- Twitter: 2-second delays

### Platform Restrictions
- **Instagram**: May require login for some features
- **Twitter**: API access limited without authentication
- **LinkedIn**: May block automated access
- **Facebook**: Anti-bot measures in place

### Legal Considerations
- **Respect ToS**: Follow platform terms of service
- **Rate Limits**: Don't overload platforms
- **Privacy**: Only search public information
- **Ethical Use**: Use responsibly

## 🚨 Troubleshooting

### Common Issues
1. **No Results**: Platform may be blocking requests
2. **Rate Limited**: Wait longer between searches
3. **Selenium Errors**: Check Chrome installation
4. **API Errors**: Verify network connection

### Solutions
- **Use VPN**: If IP is blocked
- **Reduce Frequency**: Longer delays between searches
- **Update Dependencies**: Keep packages current
- **Check Network**: Ensure stable internet connection

## 🎯 Use Cases

- **OSINT**: Open source intelligence gathering
- **Research**: Academic or professional research
- **Social Media Audit**: Brand monitoring
- **Investigation**: Legal or security investigations
- **Personal Use**: Finding your own profiles

## 🚀 Quick Start

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Run basic scraper**: `python real_social_scraper.py`
3. **Enter a name**: Type the person's name you want to search
4. **View results**: See real profiles found across platforms
5. **Save results**: Option to save to JSON file

This is a **real web scraper** that actually searches online platforms to find genuine social media profiles! 