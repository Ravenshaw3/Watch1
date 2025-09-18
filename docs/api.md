# API Documentation

Watch1 Media Server provides a comprehensive REST API for managing media files, users, and playlists.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Getting a Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=your_username&password=your_password"
```

## API Endpoints

### Authentication

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string (optional)"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST /auth/login
Authenticate user and get access token.

**Request Body:**
```
username=your_username&password=your_password
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### GET /auth/me
Get current user information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-01T12:00:00Z"
}
```

### Media Files

#### GET /media
Get list of media files with optional filtering and pagination.

**Query Parameters:**
- `query` (string, optional): Search query
- `media_type` (string, optional): Filter by media type (video, audio, image)
- `genre` (string, optional): Filter by genre
- `year` (integer, optional): Filter by year
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 20): Items per page
- `sort_by` (string, default: "created_at"): Sort field
- `sort_order` (string, default: "desc"): Sort order (asc, desc)

**Example:**
```bash
curl "http://localhost:8000/api/v1/media?media_type=video&page=1&page_size=10"
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "filename": "movie.mp4",
      "original_filename": "movie.mp4",
      "file_path": "/app/media/movie.mp4",
      "file_size": 1048576000,
      "file_hash": "abc123...",
      "mime_type": "video/mp4",
      "media_type": "video",
      "duration": 7200.5,
      "width": 1920,
      "height": 1080,
      "bitrate": 5000000,
      "codec": "h264",
      "container_format": "mp4",
      "thumbnail_path": "/app/thumbnails/movie_thumb.jpg",
      "is_processed": true,
      "is_available": true,
      "processing_status": "completed",
      "created_at": "2024-01-01T00:00:00Z",
      "metadata": {
        "id": 1,
        "title": "Amazing Movie",
        "description": "A great movie",
        "genre": "Action",
        "year": 2023,
        "director": "John Director",
        "cast": ["Actor 1", "Actor 2"],
        "rating": "PG-13"
      }
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10
}
```

#### GET /media/{id}
Get a specific media file by ID.

**Response:**
```json
{
  "id": 1,
  "filename": "movie.mp4",
  "original_filename": "movie.mp4",
  "file_path": "/app/media/movie.mp4",
  "file_size": 1048576000,
  "file_hash": "abc123...",
  "mime_type": "video/mp4",
  "media_type": "video",
  "duration": 7200.5,
  "width": 1920,
  "height": 1080,
  "bitrate": 5000000,
  "codec": "h264",
  "container_format": "mp4",
  "thumbnail_path": "/app/thumbnails/movie_thumb.jpg",
  "is_processed": true,
  "is_available": true,
  "processing_status": "completed",
  "created_at": "2024-01-01T00:00:00Z",
  "metadata": {
    "id": 1,
    "title": "Amazing Movie",
    "description": "A great movie",
    "genre": "Action",
    "year": 2023,
    "director": "John Director",
    "cast": ["Actor 1", "Actor 2"],
    "rating": "PG-13"
  }
}
```

#### POST /media/upload
Upload a new media file.

**Request:**
```
Content-Type: multipart/form-data
file: <file>
```

**Response:**
```json
{
  "file_id": 1,
  "filename": "movie.mp4",
  "status": "uploaded",
  "message": "File uploaded successfully"
}
```

#### DELETE /media/{id}
Delete a media file.

**Response:**
```json
{
  "message": "Media file deleted successfully"
}
```

#### GET /media/{id}/stream
Stream a media file.

**Response:**
```
Content-Type: video/mp4 (or appropriate media type)
Content-Length: <file_size>
Accept-Ranges: bytes

<file_content>
```

### Playlists

#### GET /playlists
Get user's playlists.

**Response:**
```json
[
  {
    "id": 1,
    "name": "My Favorites",
    "description": "My favorite movies",
    "owner_id": 1,
    "is_public": false,
    "is_smart": false,
    "created_at": "2024-01-01T00:00:00Z",
    "items": [
      {
        "id": 1,
        "playlist_id": 1,
        "media_file_id": 1,
        "position": 1,
        "added_at": "2024-01-01T00:00:00Z"
      }
    ]
  }
]
```

#### POST /playlists
Create a new playlist.

**Request Body:**
```json
{
  "name": "New Playlist",
  "description": "Playlist description",
  "is_public": false,
  "is_smart": false,
  "smart_filters": {}
}
```

**Response:**
```json
{
  "id": 1,
  "name": "New Playlist",
  "description": "Playlist description",
  "owner_id": 1,
  "is_public": false,
  "is_smart": false,
  "created_at": "2024-01-01T00:00:00Z",
  "items": []
}
```

#### GET /playlists/{id}
Get a specific playlist.

#### PUT /playlists/{id}
Update a playlist.

#### DELETE /playlists/{id}
Delete a playlist.

### Users

#### GET /users/me
Get current user profile.

#### PUT /users/me
Update current user profile.

**Request Body:**
```json
{
  "username": "new_username",
  "email": "new_email@example.com",
  "full_name": "New Full Name"
}
```

## Error Responses

All API endpoints return consistent error responses:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE"
}
```

### Common Error Codes

- `MEDIA_FILE_NOT_FOUND`: Media file with specified ID not found
- `UNSUPPORTED_MEDIA_FORMAT`: Media format not supported
- `MEDIA_PROCESSING_ERROR`: Error during media processing
- `USER_NOT_FOUND`: User with specified ID not found
- `AUTHENTICATION_ERROR`: Authentication failed
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `VALIDATION_ERROR`: Request validation failed

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## Rate Limiting

API endpoints are rate limited:

- **General API**: 10 requests per second
- **Authentication**: 1 request per second
- **File Upload**: 5 requests per minute

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Response Headers:**
```
X-Total-Count: 100
X-Page-Count: 5
X-Current-Page: 1
X-Per-Page: 20
```

## Filtering and Sorting

### Filtering

Most list endpoints support filtering:

```bash
# Filter by media type
GET /media?media_type=video

# Filter by genre
GET /media?genre=Action

# Filter by year
GET /media?year=2023

# Multiple filters
GET /media?media_type=video&genre=Action&year=2023
```

### Sorting

Sort results using `sort_by` and `sort_order`:

```bash
# Sort by creation date (newest first)
GET /media?sort_by=created_at&sort_order=desc

# Sort by filename (alphabetical)
GET /media?sort_by=filename&sort_order=asc

# Sort by duration (longest first)
GET /media?sort_by=duration&sort_order=desc
```

## WebSocket Support

Real-time features are available via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/');

ws.onopen = function() {
    console.log('Connected to WebSocket');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

### WebSocket Events

- `media_processing_started`: Media processing started
- `media_processing_completed`: Media processing completed
- `media_processing_failed`: Media processing failed
- `user_activity`: User activity updates

## SDKs and Libraries

### JavaScript/TypeScript

```bash
npm install watch1-client
```

```javascript
import { Watch1Client } from 'watch1-client';

const client = new Watch1Client({
  baseUrl: 'http://localhost:8000/api/v1',
  token: 'your-jwt-token'
});

// Get media files
const media = await client.media.getMediaFiles();

// Upload file
const result = await client.media.uploadFile(file);
```

### Python

```bash
pip install watch1-python
```

```python
from watch1 import Watch1Client

client = Watch1Client(
    base_url='http://localhost:8000/api/v1',
    token='your-jwt-token'
)

# Get media files
media = client.media.get_media_files()

# Upload file
result = client.media.upload_file(file_path)
```

## Testing the API

### Using curl

```bash
# Get media files
curl -H "Authorization: Bearer <token>" \
     "http://localhost:8000/api/v1/media"

# Upload file
curl -H "Authorization: Bearer <token>" \
     -F "file=@movie.mp4" \
     "http://localhost:8000/api/v1/media/upload"
```

### Using Postman

1. Import the API collection
2. Set the base URL: `http://localhost:8000/api/v1`
3. Add authentication token to headers
4. Test endpoints

### Interactive Documentation

Visit `http://localhost:8000/api/docs` for interactive API documentation with Swagger UI.
