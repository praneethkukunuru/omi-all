#!/usr/bin/env python3
"""
Psychological Lie Detection Framework

Advanced lie detection system based on psychological analysis patterns, linguistic cues, 
and behavioral indicators rather than fact-checking. Uses research-backed psychological 
frameworks to analyze deception in text.

Features:
- Uncertainty marker detection
- Self-reference analysis  
- Overcompensation detection
- Defensive language patterns
- Distancing language analysis
- Memory evasion indicators

No external dependencies required - uses only Python standard library.
"""

import re
import time
from typing import List, Dict
from collections import Counter

class PsychologicalLieDetector:
    def __init__(self):
        # Deception patterns from psychology research
        self.deception_patterns = {
            'uncertainty': [
                'i think', 'i believe', 'i guess', 'maybe', 'perhaps', 
                'possibly', 'probably', 'might', 'could', 'sort of', 'kind of'
            ],
            'distancing': [
                'that person', 'they', 'them', 'over there', 'that place'
            ],
            'overcompensation': [
                'honestly', 'frankly', 'to be honest', 'truthfully', 
                'believe me', 'trust me', 'i swear', 'i would never'
            ],
            'defensive': [
                'why would i', 'that\'s ridiculous', 'that\'s crazy', 
                'how dare you', 'i can\'t believe'
            ],
            'evasive': [
                'that depends', 'it\'s complicated', 'it\'s hard to say', 
                'um', 'uh', 'well'
            ],
            'memory_issues': [
                'i don\'t remember', 'i can\'t recall', 'i forget', 
                'if i recall', 'as i remember'
            ]
        }
    
    def analyze_text(self, text: str) -> Dict:
        """Analyze text for deception indicators"""
        
        text_lower = text.lower()
        words = text.split()
        
        # Count deception indicators
        indicators_found = {}
        total_indicators = 0
        
        for category, patterns in self.deception_patterns.items():
            count = 0
            for pattern in patterns:
                count += len(re.findall(r'\b' + pattern.replace(' ', r'\s+') + r'\b', text_lower))
            
            if count > 0:
                indicators_found[category] = count
                total_indicators += count
        
        # Calculate scores
        word_count = len(words)
        indicator_density = total_indicators / word_count if word_count > 0 else 0
        
        # Psychological indicators
        uncertainty_score = sum(1 for pattern in self.deception_patterns['uncertainty'] 
                               if pattern in text_lower) / len(words) if words else 0
        
        # Self-reference analysis
        first_person = len(re.findall(r'\b(i|me|my|myself)\b', text_lower))
        third_person = len(re.findall(r'\b(he|she|they|them)\b', text_lower))
        
        self_reference_ratio = first_person / (first_person + third_person) if (first_person + third_person) > 0 else 0.5
        
        # Calculate deception probability
        deception_score = 0
        
        # High uncertainty increases deception probability
        if uncertainty_score > 0.05:
            deception_score += 0.3
        
        # Low self-reference increases deception probability
        if self_reference_ratio < 0.3:
            deception_score += 0.2
        
        # Multiple indicator types increase probability
        if len(indicators_found) > 2:
            deception_score += 0.2
        
        # High indicator density
        if indicator_density > 0.1:
            deception_score += 0.3
        
        # Specific high-risk patterns
        if 'overcompensation' in indicators_found:
            deception_score += 0.4
        if 'defensive' in indicators_found:
            deception_score += 0.3
        
        deception_probability = min(deception_score, 1.0)
        
        return {
            'text': text,
            'deception_probability': deception_probability,
            'is_deceptive': deception_probability > 0.5,
            'confidence': abs(deception_probability - 0.5) * 2,
            'indicators_found': indicators_found,
            'total_indicators': total_indicators,
            'uncertainty_score': uncertainty_score,
            'self_reference_ratio': self_reference_ratio,
            'word_count': word_count,
            'analysis_details': {
                'indicator_density': indicator_density,
                'risk_level': self._get_risk_level(deception_probability)
            }
        }
    
    def _get_risk_level(self, probability: float) -> str:
        """Get risk level description"""
        if probability > 0.8:
            return "Very High Risk"
        elif probability > 0.6:
            return "High Risk"
        elif probability > 0.4:
            return "Medium Risk"
        elif probability > 0.2:
            return "Low Risk"
        else:
            return "Very Low Risk"
    
    def print_result(self, result: Dict):
        """Print analysis result"""
        
        print(f"\n📝 Text: \"{result['text'][:80]}{'...' if len(result['text']) > 80 else ''}\"")
        print("=" * 60)
        
        # Overall assessment
        status = "🚨 LIKELY DECEPTIVE" if result['is_deceptive'] else "✅ LIKELY TRUTHFUL"
        print(f"{status}")
        print(f"📊 Deception Probability: {result['deception_probability']:.1%}")
        print(f"🎯 Confidence: {result['confidence']:.1%}")
        print(f"⚠️  Risk Level: {result['analysis_details']['risk_level']}")
        
        # Detailed analysis
        print(f"\n🔍 Analysis Details:")
        print(f"   • Word Count: {result['word_count']}")
        print(f"   • Total Indicators: {result['total_indicators']}")
        print(f"   • Uncertainty Score: {result['uncertainty_score']:.1%}")
        print(f"   • Self-Reference Ratio: {result['self_reference_ratio']:.1%}")
        
        # Indicators found
        if result['indicators_found']:
            print(f"\n⚠️  Deception Indicators Found:")
            for category, count in result['indicators_found'].items():
                print(f"   • {category.replace('_', ' ').title()}: {count} instance(s)")
        else:
            print(f"\n✅ No major deception indicators found")
        
        print("\n" + "=" * 60)

def run_test():
    """Run comprehensive test of lie detector"""
    
    print("🔍 Psychological Lie Detection Test")
    print("=" * 50)
    print("Testing with various text samples...")
    print("=" * 50)
    
    detector = PsychologicalLieDetector()
    
    # Test samples with expected results
    test_samples = [
        {
            'text': "I was at home all evening watching Netflix with my family.",
            'expected': "Truthful",
            'description': "Simple, direct statement"
        },
        {
            'text': "I think I was probably at home, maybe watching TV or something. I don't really remember exactly what I was doing.",
            'expected': "Deceptive", 
            'description': "High uncertainty, vague details"
        },
        {
            'text': "Why would you even ask me that? I told you I was home! Don't you trust me? That's ridiculous!",
            'expected': "Deceptive",
            'description': "Defensive, confrontational"
        },
        {
            'text': "To be honest, I definitely was at home the whole time. You can trust me on this. I would never lie to you.",
            'expected': "Deceptive",
            'description': "Overcompensation, credibility boosters"
        },
        {
            'text': "I went to the store around 3 PM, bought milk and bread, then came straight home.",
            'expected': "Truthful",
            'description': "Specific details, clear timeline"
        },
        {
            'text': "That person said they saw someone who looked like me, but I don't think it was actually me there.",
            'expected': "Deceptive",
            'description': "Distancing language, third person"
        }
    ]
    
    correct_predictions = 0
    total_tests = len(test_samples)
    
    for i, sample in enumerate(test_samples, 1):
        print(f"\n🧪 Test {i}: {sample['description']}")
        print(f"Expected: {sample['expected']}")
        
        result = detector.analyze_text(sample['text'])
        detector.print_result(result)
        
        # Check if prediction matches expectation
        predicted = "Deceptive" if result['is_deceptive'] else "Truthful"
        is_correct = predicted == sample['expected']
        
        if is_correct:
            correct_predictions += 1
            print("✅ CORRECT PREDICTION")
        else:
            print("❌ INCORRECT PREDICTION")
        
        print(f"Predicted: {predicted} | Expected: {sample['expected']}")
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print(f"\n📊 TEST RESULTS SUMMARY")
    print("=" * 40)
    print(f"Total Tests: {total_tests}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Accuracy: {correct_predictions/total_tests:.1%}")
    print(f"Incorrect Predictions: {total_tests - correct_predictions}")
    
    if correct_predictions >= total_tests * 0.7:
        print("🎉 GOOD PERFORMANCE - System working well!")
    elif correct_predictions >= total_tests * 0.5:
        print("⚠️  MODERATE PERFORMANCE - Needs tuning")
    else:
        print("❌ POOR PERFORMANCE - Requires adjustment")

def interactive_test():
    """Interactive test where user can input their own text"""
    
    print("\n🔍 Interactive Lie Detection Test")
    print("=" * 40)
    print("Enter your own text to analyze...")
    
    detector = PsychologicalLieDetector()
    
    while True:
        text = input("\nEnter text to analyze (or 'quit' to exit): ").strip()
        
        if text.lower() in ['quit', 'exit', 'q']:
            break
        
        if not text:
            print("Please enter some text to analyze")
            continue
        
        result = detector.analyze_text(text)
        detector.print_result(result)

if __name__ == "__main__":
    print("🚀 Starting Lie Detector Test Suite")
    print("=" * 50)
    
    # Run automated tests
    run_test()
    
    # Ask if user wants interactive test
    interactive = input("\nRun interactive test? (y/n): ").lower()
    if interactive == 'y':
        interactive_test()
    
    print("\n🎯 Test Complete!")
    print("The lie detector uses psychological patterns to detect deception")
    print("including uncertainty markers, distancing language, overcompensation,")
    print("defensive responses, and other research-backed indicators.") 