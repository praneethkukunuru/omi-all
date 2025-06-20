const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const { RNNodeJsMobile } = require('nodejs-mobile-react-native');
const wav = require('wav');

const app = express();
const port = 3000;

// Middleware to handle raw body for audio stream
app.use(bodyParser.raw({ type: 'application/octet-stream', limit: '50mb' }));

app.post('/audio', (req, res) => {
  console.log('Received audio data POST request');
  
  if (!req.body || req.body.length === 0) {
    console.error('No audio data received in request body');
    return res.status(400).send('No audio data received.');
  }

  const sampleRate = parseInt(req.query.sample_rate || '16000', 10);
  const uid = req.query.uid || 'unknown_user';
  const timestamp = new Date().getTime();
  const filename = `omi_audio_${timestamp}.wav`;
  
  // The library expects files to be in the `Documents` directory
  const audioDir = path.join(RNNodeJsMobile.getDocumentDirectoryPath(), 'AudioFiles');
  const filePath = path.join(audioDir, filename);

  console.log(`Attempting to save to: ${filePath}`);

  // Ensure the directory exists
  if (!fs.existsSync(audioDir)) {
    console.log('AudioFiles directory does not exist, creating it.');
    fs.mkdirSync(audioDir, { recursive: true });
  }

  try {
    // Use the 'wav' library to create a proper WAV file
    const fileWriter = new wav.FileWriter(filePath, {
      channels: 1,
      sampleRate: sampleRate,
      bitDepth: 16
    });

    fileWriter.write(req.body, (err) => {
      if (err) {
        console.error('Error writing WAV file chunk:', err);
        // Clean up partially written file
        fs.unlink(filePath, () => {});
        return res.status(500).send('Error processing audio data.');
      }

      fileWriter.end((err) => {
        if (err) {
          console.error('Error finalizing WAV file:', err);
          return res.status(500).send('Error finalizing audio file.');
        }
        
        console.log(`Successfully saved WAV file: ${filename}`);
        
        // Notify the React Native UI that a new file is ready
        RNNodeJsMobile.channel.send({
          type: 'new_audio_file',
          payload: {
            filename: filename,
            path: filePath,
            receivedDate: new Date().toISOString(),
            sampleRate: sampleRate,
            uid: uid
          }
        });
        
        res.status(200).json({ status: 'ok', filename: filename });
      });
    });
  } catch (error) {
    console.error('An unexpected error occurred:', error);
    res.status(500).send('An internal server error occurred.');
  }
});

app.get('/ping', (req, res) => {
  console.log('Received ping request');
  res.status(200).send('pong');
});

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
  // Notify the React Native UI that the server is running
  RNNodeJsMobile.channel.send({ type: 'server_started', payload: { port: port } });
}); 