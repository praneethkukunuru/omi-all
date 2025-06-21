# Comprehensive Person Finder

An advanced person search tool that aggregates information from multiple sources to build a complete profile of a person based on their name.

## 🌟 Features

### Multi-Platform Search
- **LinkedIn**: Professional profiles, work history, education, skills
- **Instagram**: Social profiles, followers, posts, bio information
- **Twitter**: Social media presence and mentions
- **Facebook**: Public profile information
- **Web Mentions**: Articles, news, press releases, directory listings

### Advanced Data Aggregation
- **Professional Information**: Job titles, companies, career history
- **Educational Background**: Schools, degrees, certifications
- **Skills & Expertise**: Technical and soft skills from various sources
- **Location Data**: Current and past locations
- **Social Connections**: Mentions and associations
- **Interests & Hobbies**: Extracted from social media profiles

### Smart Analysis
- **Confidence Scoring**: Each result gets a confidence score based on name matching
- **Data Correlation**: Connects information across platforms
- **Relevance Ranking**: Sorts results by relevance and confidence
- **Duplicate Detection**: Removes duplicate profiles and information

## 🚀 Usage

### Basic Search
```python
from comprehensive_person_finder import ComprehensivePersonFinder

finder = ComprehensivePersonFinder()
person_data = finder.comprehensive_search("John Smith")
finder.print_comprehensive_results(person_data)
```

### Advanced Search with Location
```python
person_data = finder.comprehensive_search(
    name="Jane Doe", 
    location="San Francisco",
    additional_info="CEO tech startup"
)
```

### Command Line Usage
```bash
python comprehensive_person_finder.py
```

## 📊 Data Structure

The finder returns a `PersonData` object containing:

```python
@dataclass
class PersonData:
    name: str
    profiles: List[PersonProfile]           # Social media profiles
    web_mentions: List[WebMention]          # Web articles and mentions
    professional_info: Dict[str, Any]       # Professional background
    contact_info: Dict[str, str]            # Contact information
    education: List[Dict[str, str]]         # Educational background
    work_history: List[Dict[str, str]]      # Career history
    skills: List[str]                       # Skills and expertise
    interests: List[str]                    # Interests and hobbies
    locations: Set[str]                     # Associated locations
    confidence_score: float                 # Overall confidence (0-1)
```

## 🔍 Search Methods

### 1. Social Media Search
- Direct platform API searches where available
- Web scraping for public information
- Username pattern matching and variations
- Bio and description analysis

### 2. Professional Network Search
- LinkedIn profile discovery
- Professional directory searches
- Company and organization affiliations
- Industry-specific databases

### 3. Web Mention Analysis
- Google search result analysis
- News article and press release search
- Professional publication mentions
- Directory and listing appearances

### 4. Cross-Platform Correlation
- Name matching across platforms
- Location consistency checking
- Professional information verification
- Timeline and career progression analysis

## 📈 Confidence Scoring

Each piece of information gets a confidence score based on:
- **Name Similarity**: How closely the found name matches the search query
- **Platform Reliability**: More weight given to professional platforms
- **Information Consistency**: Cross-platform verification
- **Profile Completeness**: More complete profiles get higher scores

## 🛡️ Privacy & Ethics

- **Public Information Only**: Only searches publicly available information
- **Rate Limiting**: Respects platform rate limits and terms of service
- **No Authentication**: Does not require login credentials
- **Ethical Usage**: Designed for legitimate research and networking purposes

## ⚠️ Limitations

- **Platform Restrictions**: Some platforms limit public access
- **Rate Limiting**: Search speed limited by platform restrictions
- **Privacy Settings**: Cannot access private or restricted profiles
- **Data Accuracy**: Information accuracy depends on source quality
- **Geographic Bias**: Better results for English-speaking regions

## 🔧 Configuration

### Search Parameters
- `max_results_per_platform`: Limit results per platform (default: 10)
- `timeout`: Request timeout in seconds (default: 15)
- `rate_limit_delay`: Delay between requests (default: 1-2 seconds)

### Customizable Searches
- Professional focus: Emphasize LinkedIn and business directories
- Social focus: Prioritize social media platforms
- Academic focus: Target academic and research platforms

## 📋 Output Formats

### Console Output
- Formatted text output with confidence scores
- Platform-organized results
- Summary statistics

### JSON Export
```python
finder.save_comprehensive_results(person_data, "search_results.json")
```

### CSV Export (optional)
- Structured data for analysis
- Compatible with spreadsheet applications

## 🔒 Privacy Considerations

- Only searches publicly available information
- Respects robots.txt and platform terms of service
- No data storage beyond session
- Option to anonymize sensitive information

## 🚀 Advanced Features

### Batch Processing
```python
names = ["John Smith", "Jane Doe", "Bob Johnson"]
results = finder.batch_search(names)
```

### Custom Search Patterns
```python
finder.add_custom_pattern("company_ceo", "{name} CEO {company}")
```

### Integration with Other Tools
- Export to CRM systems
- API endpoint creation
- Database integration options

## 🔍 Example Output

```
👤 Comprehensive Profile for: John Smith
================================================================================
🎯 Overall Confidence Score: 85.2%
📍 Locations: San Francisco, CA; New York, NY

📱 Social Media Profiles (4 found):
--------------------------------------------------

🔹 LinkedIn: @johnsmith-tech ✓
   Name: John Smith
   URL: https://linkedin.com/in/johnsmith-tech
   Bio: Senior Software Engineer at TechCorp
   Location: San Francisco, CA
   Confidence: 92.1%

🔹 Instagram: @johnsmith_sf
   Name: John Smith
   URL: https://instagram.com/johnsmith_sf
   Bio: Tech enthusiast | Coffee lover | SF
   Followers: 1,247
   Confidence: 78.3%

💼 Professional Information:
--------------------------------------------------

🏢 Work History (from LinkedIn):
   • Senior Software Engineer at TechCorp
   • Software Engineer at StartupXYZ
   • Junior Developer at WebCompany

🎓 Education (from LinkedIn):
   • Bachelor of Science in Computer Science at UC Berkeley

🛠️ Skills (12):
   Python, JavaScript, React, Node.js, AWS, Docker, Git, MongoDB, SQL, Agile, 
   Machine Learning, Data Analysis

🌐 Web Mentions (8 found):
--------------------------------------------------

🔗 Article: John Smith Speaks at Tech Conference 2023
   URL: https://techblog.com/john-smith-conference-2023
   Snippet: Senior engineer John Smith presented his insights on...
   Relevance: 94.7%
```

## 📝 Installation

```bash
pip install -r requirements.txt
python comprehensive_person_finder.py
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional platform integrations
- Better name matching algorithms
- Enhanced data correlation
- Performance optimizations

## ⚖️ Legal Notice

This tool is designed for legitimate research and networking purposes only. Users must:
- Respect platform terms of service
- Comply with local privacy laws
- Use information ethically and responsibly
- Obtain consent when required

## 📞 Support

For questions or issues, please refer to the documentation or submit an issue. 