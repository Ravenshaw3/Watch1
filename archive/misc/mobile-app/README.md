# Watch1 Mobile App

A React Native mobile app for the Watch1 Media Server with full TV series playback, playlist management, and beautiful UI.

## 🚀 Features

### 📱 **Mobile-Optimized Experience**
- **Native mobile app** built with React Native and Expo
- **Touch-friendly interface** with haptic feedback
- **Offline support** for downloaded content
- **Background playback** for audio content
- **Picture-in-picture** mode for video

### 🎬 **TV Series Playback**
- **Back-to-back episode playback** with auto-advance
- **Season and episode browsing** with beautiful cards
- **Progress tracking** across episodes
- **Resume playback** from where you left off
- **Skip intro/outro** functionality

### 🎵 **Playlist Management**
- **Create and manage playlists** on mobile
- **Drag-and-drop reordering** of playlist items
- **Shuffle and repeat modes**
- **Cross-device sync** with web app
- **Offline playlist support**

### 🎨 **Beautiful UI**
- **Dark/light theme** support
- **Smooth animations** and transitions
- **Gesture-based controls** for video player
- **Customizable color schemes**
- **Responsive design** for all screen sizes

## 📦 Installation

### Prerequisites
- Node.js 18+
- Expo CLI: `npm install -g @expo/cli`
- iOS Simulator (for iOS development)
- Android Studio (for Android development)

### Setup
```bash
# Install dependencies
npm install

# Start development server
npm start

# Run on iOS
npm run ios

# Run on Android
npm run android

# Build for production
npm run build:ios
npm run build:android
```

## 🔧 Configuration

### API Configuration
Update `src/config/api.ts` with your Watch1 server URL:
```typescript
export const API_BASE_URL = 'http://192.168.254.14:8000/api/v1';
```

### Authentication
The app uses JWT tokens for authentication, automatically syncing with your web login.

## 📱 App Structure

```
src/
├── screens/           # App screens
│   ├── HomeScreen.tsx
│   ├── LibraryScreen.tsx
│   ├── TVSeriesScreen.tsx
│   ├── PlaylistsScreen.tsx
│   ├── PlayerScreen.tsx
│   └── LoginScreen.tsx
├── components/        # Reusable components
├── services/          # API services
├── store/            # Redux store
├── types/            # TypeScript types
└── utils/            # Utility functions
```

## 🎯 Key Features

### **Video Player**
- Full-screen video playback
- Gesture controls (tap to play/pause, swipe for seek)
- Picture-in-picture mode
- Background audio playback
- Auto-advance to next episode

### **TV Series**
- Browse by series and season
- Episode thumbnails and metadata
- Progress tracking
- Continue watching
- Recently watched

### **Playlists**
- Create and edit playlists
- Add/remove items
- Reorder with drag-and-drop
- Shuffle and repeat modes
- Offline support

### **Offline Support**
- Download episodes for offline viewing
- Sync progress across devices
- Background downloads
- Storage management

## 🚀 Future Enhancements

### **Planned Features**
- **Cast to TV** (Chromecast, AirPlay)
- **Download for offline** viewing
- **Parental controls** and content filtering
- **Multiple user profiles** on same device
- **Voice search** and commands
- **Smart recommendations** based on viewing history
- **Social features** (share playlists, rate content)
- **Live TV** and streaming integration
- **Podcast support** with chapter navigation
- **Audiobook player** with sleep timer

### **Advanced Features**
- **AI-powered recommendations**
- **Content discovery** with trending/popular
- **Watch parties** with friends
- **Content rating** and reviews
- **Advanced search** with filters
- **Bulk operations** (add multiple items to playlist)
- **Export/import** playlists
- **Backup and restore** settings

## 📱 Platform Support

- **iOS 13+** (iPhone, iPad)
- **Android 8+** (Phone, Tablet)
- **Web** (Progressive Web App)

## 🔒 Security

- **JWT authentication** with refresh tokens
- **Secure API communication** (HTTPS)
- **Local data encryption** for sensitive info
- **Biometric authentication** (Face ID, Touch ID, Fingerprint)

## 📊 Analytics

- **Viewing analytics** and progress tracking
- **Usage statistics** and insights
- **Performance monitoring**
- **Crash reporting**

## 🎨 Customization

- **Multiple themes** (Dark, Light, Auto)
- **Custom color schemes**
- **Font size adjustment**
- **Layout preferences** (Grid, List)
- **Accessibility features**

## 📱 Download

The mobile app will be available on:
- **App Store** (iOS)
- **Google Play Store** (Android)
- **Direct APK download** (Android)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Documentation**: [docs.watch1.com](https://docs.watch1.com)
- **Issues**: GitHub Issues
- **Discord**: [discord.gg/watch1](https://discord.gg/watch1)
- **Email**: support@watch1.com

