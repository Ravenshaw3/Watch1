# Watch 1 - High-Performance Media Server

A next-generation media server built with modern technologies for handling large media libraries with advanced features.

## 🚀 Features

### Core Features
- **High-Performance Backend**: FastAPI with async/await for maximum concurrency
- **Modern Frontend**: Vue.js 3 with TypeScript for smooth user experience
- **Docker Architecture**: Microservices with separate backend and frontend containers
- **Large Library Support**: Optimized for 10,000+ media files

### Advanced Media Management (Feature 10)
- Drag & drop file organization
- Batch operations (delete, move, rename)
- Smart collections and playlists
- Advanced metadata editing
- Duplicate file detection
- Smart folder organization

### Enhanced Player (Feature 11)
- Picture-in-picture mode
- Multiple subtitle tracks
- Audio track selection
- Playback speed control
- Keyboard shortcuts
- Advanced video controls

### Smart Features (Feature 12)
- AI-powered recommendations
- Automatic genre detection
- Smart search with filters
- Content-based recommendations
- Usage analytics and insights

## 🏗️ Architecture

```
Watch1/
├── backend/          # FastAPI backend service
├── frontend/         # Vue.js frontend application
├── docker-compose.yml # Multi-container setup
├── nginx/            # Reverse proxy configuration
└── docs/             # Documentation
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **PostgreSQL**: High-performance database
- **Redis**: Caching and session storage
- **Celery**: Background task processing
- **FFmpeg**: Media processing and transcoding

### Frontend
- **Vue.js 3**: Progressive JavaScript framework
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool
- **Pinia**: State management
- **Vue Router**: Client-side routing
- **Tailwind CSS**: Utility-first CSS framework

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy and load balancing
- **Prometheus**: Monitoring and metrics

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Watch1
   ```

2. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Configuration](docs/configuration.md)
- [API Documentation](docs/api.md)
- [Frontend Development](docs/frontend.md)
- [Deployment](docs/deployment.md)

## 🔧 Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## 📊 Performance

- **Initial Load**: < 1 second
- **Navigation**: Instant
- **Large Libraries**: Smooth scrolling for 10,000+ files
- **Search**: Real-time with < 100ms response
- **Streaming**: Optimized with range requests and caching

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern web technologies
- Inspired by Netflix and Plex
- Community-driven development
