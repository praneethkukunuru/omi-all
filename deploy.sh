#!/bin/bash

# Omi Audio Receiver Deployment Script
# This script helps deploy the webhook server for testing

echo "🚀 Omi Audio Receiver Deployment Script"
echo "========================================"

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok is not installed. Please install it first:"
    echo "   brew install ngrok (on macOS)"
    echo "   or download from https://ngrok.com/"
    exit 1
fi

# Check if the iOS app is running
echo "📱 Checking if iOS app is running..."
if pgrep -f "OmiAudioReceiver" > /dev/null; then
    echo "✅ iOS app is running"
else
    echo "⚠️  iOS app is not running. Please start it in Xcode first."
fi

# Start ngrok tunnel
echo "🌐 Starting ngrok tunnel on port 8080..."
ngrok http 8080 --log=stdout > ngrok.log 2>&1 &

# Wait a moment for ngrok to start
sleep 3

# Get the public URL
if [ -f ngrok.log ]; then
    NGROK_URL=$(grep -o 'https://[a-zA-Z0-9]*\.ngrok\.io' ngrok.log | head -1)
    if [ ! -z "$NGROK_URL" ]; then
        echo "✅ ngrok tunnel established: $NGROK_URL"
        echo ""
        echo "🔗 Webhook URL for Omi device:"
        echo "   $NGROK_URL/audio"
        echo ""
        echo "📋 Instructions:"
        echo "1. Copy the webhook URL above"
        echo "2. Open the Omi app on your device"
        echo "3. Go to Settings → Developer Mode"
        echo "4. Set 'Realtime audio bytes' to: $NGROK_URL/audio"
        echo "5. Configure frequency (e.g., every 10 seconds)"
        echo "6. Start speaking to your Omi device"
        echo ""
        echo "📊 Monitor logs: tail -f ngrok.log"
        echo "🛑 Stop tunnel: pkill ngrok"
    else
        echo "❌ Failed to get ngrok URL. Check ngrok.log for details."
    fi
else
    echo "❌ Failed to start ngrok tunnel."
fi

echo ""
echo "Press Ctrl+C to stop the tunnel"
wait 