import React, {useState, useEffect, useRef} from 'react';
import {
  SafeAreaView,
  StyleSheet,
  Text,
  View,
  FlatList,
  TouchableOpacity,
  Platform,
  PermissionsAndroid,
  ScrollView,
} from 'react-native';
import nodejs from 'nodejs-mobile-react-native';
import Sound from 'react-native-sound';
import RNFS from 'react-native-fs';

// Enable audio playback in silent mode
Sound.setCategory('Playback');

const App = () => {
  const [serverStatus, setServerStatus] = useState('Starting...');
  const [webhookUrl, setWebhookUrl] = useState('');
  const [audioFiles, setAudioFiles] = useState([]);
  const [serverLogs, setServerLogs] = useState([]);
  const [currentPlaying, setCurrentPlaying] = useState(null);
  const soundRef = useRef(null);

  const log = message => {
    console.log(message);
    setServerLogs(prev => [
      `[${new Date().toLocaleTimeString()}] ${message}`,
      ...prev,
    ]);
  };

  const loadExistingFiles = async () => {
    try {
      const audioDir = `${RNFS.DocumentDirectoryPath}/AudioFiles`;
      const dirExists = await RNFS.exists(audioDir);
      if (!dirExists) {
        log('AudioFiles directory does not exist. No files to load.');
        return;
      }

      const files = await RNFS.readDir(audioDir);
      const wavFiles = files
        .filter(file => file.name.endsWith('.wav'))
        .map(file => ({
          id: file.path,
          filename: file.name,
          path: file.path,
          receivedDate: file.mtime || new Date(),
        }))
        .sort((a, b) => b.receivedDate - a.receivedDate);

      setAudioFiles(wavFiles);
      log(`Loaded ${wavFiles.length} existing audio files.`);
    } catch (error) {
      log(`Error loading existing files: ${error.message}`);
    }
  };

  useEffect(() => {
    // This is the message listener for events from the Node.js server
    const listener = nodejs.channel.addListener('message', msg => {
      log(`Message from Node: ${JSON.stringify(msg)}`);
      if (msg.type === 'server_started') {
        setServerStatus(`Active on port ${msg.payload.port}`);
        // For local testing, you can use localhost. For device, you'd need ngrok.
        // This part is for display only; the actual URL is set up externally.
        setWebhookUrl(`http://localhost:${msg.payload.port}/audio`);
      }
      if (msg.type === 'new_audio_file') {
        setAudioFiles(prev => [
          {id: msg.payload.path, ...msg.payload},
          ...prev,
        ]);
      }
    });

    // Start the Node.js server
    nodejs.start('main.js');
    log('Node.js background server started.');

    // Load any files that were saved from previous sessions
    loadExistingFiles();

    // Request permissions on Android
    if (Platform.OS === 'android') {
      requestStoragePermission();
    }

    return () => {
      listener.remove();
      // Consider if you want to stop the server on component unmount
      // nodejs.stop();
    };
  }, []);

  const requestStoragePermission = async () => {
    try {
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.WRITE_EXTERNAL_STORAGE,
        {
          title: 'Storage Permission Needed',
          message: 'This app needs access to your storage to save audio files.',
          buttonNeutral: 'Ask Me Later',
          buttonNegative: 'Cancel',
          buttonPositive: 'OK',
        },
      );
      if (granted !== PermissionsAndroid.RESULTS.GRANTED) {
        log('Storage permission denied.');
      }
    } catch (err) {
      console.warn(err);
    }
  };

  const playSound = file => {
    if (soundRef.current) {
      soundRef.current.release();
    }

    const sound = new Sound(file.path, '', error => {
      if (error) {
        log(`Failed to load the sound: ${error.message}`);
        return;
      }
      setCurrentPlaying(file.id);
      sound.play(success => {
        if (!success) {
          log('Playback failed due to audio decoding errors.');
        }
        setCurrentPlaying(null);
        sound.release();
        soundRef.current = null;
      });
    });
    soundRef.current = sound;
  };

  const stopSound = () => {
    if (soundRef.current) {
      soundRef.current.stop(() => {
        soundRef.current.release();
        soundRef.current = null;
        setCurrentPlaying(null);
      });
    }
  };

  const renderItem = ({item}) => (
    <View style={styles.fileItem}>
      <View style={styles.fileInfo}>
        <Text style={styles.fileName}>{item.filename}</Text>
        <Text style={styles.fileDate}>
          Received: {new Date(item.receivedDate).toLocaleString()}
        </Text>
      </View>
      <TouchableOpacity
        style={styles.playButton}
        onPress={() =>
          currentPlaying === item.id ? stopSound() : playSound(item)
        }>
        <Text style={styles.playButtonText}>
          {currentPlaying === item.id ? 'Stop' : 'Play'}
        </Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Omi Audio Receiver</Text>
        <Text style={styles.status}>Server Status: {serverStatus}</Text>
      </View>

      <View style={styles.webhookSection}>
        <Text style={styles.sectionTitle}>Your Webhook URL</Text>
        <Text style={styles.urlText} selectable>
          {webhookUrl || 'Waiting for server...'}
        </Text>
        <Text style={styles.urlInstructions}>
          Use a service like ngrok to expose this URL to the internet, then
          paste the public URL into your Omi device settings.
        </Text>
      </View>

      <View style={styles.filesSection}>
        <Text style={styles.sectionTitle}>Received Audio Files</Text>
        <FlatList
          data={audioFiles}
          renderItem={renderItem}
          keyExtractor={item => item.id}
          ListEmptyComponent={
            <Text style={styles.emptyText}>No audio files received yet.</Text>
          }
        />
      </View>

      <View style={styles.logsSection}>
        <Text style={styles.sectionTitle}>Logs</Text>
        <ScrollView style={styles.logContainer} nestedScrollEnabled>
          {serverLogs.map((logMsg, index) => (
            <Text key={index} style={styles.logText}>
              {logMsg}
            </Text>
          ))}
        </ScrollView>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f2f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1c1e21',
  },
  status: {
    fontSize: 16,
    color: '#606770',
    marginTop: 4,
  },
  webhookSection: {
    backgroundColor: '#ffffff',
    margin: 16,
    padding: 16,
    borderRadius: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#1c1e21',
  },
  urlText: {
    fontSize: 14,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    color: '#333',
    backgroundColor: '#e7f3ff',
    padding: 8,
    borderRadius: 4,
  },
  urlInstructions: {
    fontSize: 12,
    color: '#606770',
    marginTop: 8,
  },
  filesSection: {
    flex: 1,
    margin: 16,
    marginTop: 0,
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 16,
  },
  fileItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  fileInfo: {
    flex: 1,
  },
  fileName: {
    fontSize: 16,
    color: '#1c1e21',
  },
  fileDate: {
    fontSize: 12,
    color: '#606770',
  },
  playButton: {
    backgroundColor: '#1877f2',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 6,
  },
  playButtonText: {
    color: '#ffffff',
    fontWeight: 'bold',
  },
  emptyText: {
    textAlign: 'center',
    color: '#606770',
    marginTop: 20,
  },
  logsSection: {
    height: 150,
    margin: 16,
    backgroundColor: '#333',
    borderRadius: 8,
    padding: 16,
  },
  logContainer: {
    flex: 1,
  },
  logText: {
    color: '#e0e0e0',
    fontSize: 10,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
});

export default App; 