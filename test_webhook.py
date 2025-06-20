#!/usr/bin/env python3
"""
Test script for Omi Audio Receiver webhook server
This script sends test audio data to verify the webhook is working
"""

import requests
import time
import wave
import struct
import sys
import math

def create_test_audio_data(duration_seconds=5, sample_rate=16000):
    """Create a simple test audio signal (sine wave)"""
    # Generate a 440Hz sine wave
    frequency = 440
    samples = int(duration_seconds * sample_rate)
    
    audio_data = bytearray()
    for i in range(samples):
        # Generate sine wave sample
        angle = 2 * math.pi * i * frequency / sample_rate
        sample = int(32767 * 0.3 * math.sin(angle))
        # Convert to 16-bit little-endian
        audio_data.extend(struct.pack('<h', sample))
    
    return bytes(audio_data)

def test_webhook(webhook_url, test_data):
    """Send test data to the webhook server"""
    try:
        print(f"Sending test data to: {webhook_url}")
        print(f"Data size: {len(test_data)} bytes")
        
        # Add query parameters as specified in Omi documentation
        params = {
            'sample_rate': '16000',
            'uid': 'test_user_123'
        }
        
        response = requests.post(
            webhook_url,
            data=test_data,
            params=params,
            headers={'Content-Type': 'application/octet-stream'},
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook test successful!")
            return True
        else:
            print("❌ Webhook test failed!")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending request: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_webhook.py <webhook_url>")
        print("Example: python test_webhook.py http://192.168.1.100:8080/audio")
        print("Example: python test_webhook.py https://abc123.ngrok.io/audio")
        sys.exit(1)
    
    webhook_url = sys.argv[1]
    
    print("🎵 Omi Audio Receiver - Webhook Test")
    print("=" * 40)
    
    # Create test audio data
    print("Creating test audio data...")
    test_data = create_test_audio_data(duration_seconds=3, sample_rate=16000)
    
    # Test the webhook
    success = test_webhook(webhook_url, test_data)
    
    if success:
        print("\n🎉 Webhook is working correctly!")
        print("Check your iOS app to see if the audio file was received.")
    else:
        print("\n💥 Webhook test failed!")
        print("Please check:")
        print("1. The webhook URL is correct")
        print("2. The iOS app is running")
        print("3. The webhook server is active")
        print("4. Network connectivity")

if __name__ == "__main__":
    main() 