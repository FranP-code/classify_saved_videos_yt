# YouTube Video Classifier

An AI-powered tool that automatically classifies YouTube videos in your "Watch Later" playlist based on their titles and thumbnails using vision-language models through Ollama.

## Features ✨

- 🤖 **AI-Powered Classification**: Uses Ollama with Qwen2.5-VL and fallback models to analyze video titles and thumbnails
- 🔄 **Robust LLM Integration**: Automatic fallback between models with increasing timeouts for reliability
- 📊 **Comprehensive CSV Storage**: Saves detailed video information including classifications, metadata, and thumbnails
- 🌐 **Multi-language Detection**: Automatically detects video language using AI
- 🏷️ **Smart Tagging**: Generates detailed sub-tags for better content organization
- 🎯 **Smart Categories**: Uses existing classifications or creates new ones automatically
- 🖥️ **Browser Automation**: Selenium-based interaction with YouTube for reliable data extraction
- 🎨 **Beautiful Logging**: Rich console output with colors and emojis for better UX
- ⌨️ **Easy Control**: Press 'q' at any time to safely quit the process

## Quick Start

### Prerequisites

- Python 3.11.10+
- Ollama installed locally
- Chrome or Chromium browser

### Setup

1. **Install Ollama**: Download from [https://ollama.ai](https://ollama.ai)

2. **Pull Required Models**:

   ```bash
   ollama pull qwen2.5vl:7b
   ollama pull gemma2:2b
   ```

3. **Start Ollama Service**:

   ```bash
   ollama serve
   ```

4. **Clone and Setup Project**:

   ```bash
   git clone <repository-url>
   cd youtube-video-classifier

   # Create virtual environment
   python -m venv prod
   source prod/bin/activate  # On Windows: prod\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

5. **Configure Settings** (optional):
   Edit `config.ini` to customize your setup

6. **Run the Classifier**:
   ```bash
   python script.py
   ```

## How It Works 🔄

1. **Browser Initialization**: Opens Chrome/Chromium and navigates to your YouTube "Watch Later" playlist
2. **Video Detection**: Finds and extracts information from playlist videos using Selenium
3. **Data Extraction**: Captures video title, thumbnail, channel info, duration, and upload date
4. **AI Analysis**: Uses Ollama models to:
   - Classify the video into categories
   - Detect the primary language
   - Generate detailed sub-tags
5. **Smart Fallback**: If primary model fails/times out, automatically switches to fallback model
6. **Data Storage**: Saves all information to CSV with base64-encoded thumbnails
7. **Playlist Management**: Removes processed videos from "Watch Later" playlist
8. **Continuous Processing**: Continues until all videos are processed or user quits

## Configuration

The `config.ini` file allows you to customize various settings:

```ini
[DEFAULT]
# Ollama settings
ollama_host = http://localhost:11434
ollama_model = qwen2.5vl:7b
ollama_fallback_model = gemma2:2b

# File paths
classifications_csv = video_classifications.csv
playlist_url = https://www.youtube.com/playlist?list=WL

# LLM timeout settings (in seconds)
llm_primary_timeout = 60
llm_fallback_timeout = 60

# Processing settings
enable_delete = false
enable_playlist_creation = false
```

## CSV Output Format 📋

The script creates a comprehensive CSV file with the following columns:

- `video_title`: Title of the video
- `video_url`: YouTube URL of the video
- `thumbnail_url`: Path to the saved thumbnail
- `classification`: AI-generated category
- `language`: Detected language of the video
- `channel_name`: Name of the YouTube channel
- `channel_link`: URL to the channel
- `video_length_seconds`: Duration in seconds
- `video_date`: Upload date
- `detailed_subtags`: AI-generated specific tags
- `playlist_name`: Source playlist name
- `playlist_link`: Source playlist URL
- `image_data`: Base64-encoded thumbnail data
- `timestamp`: When the classification was made

## File Structure 📁

```
├── script.py                 # Main classification script
├── config.ini               # Configuration settings
├── requirements.txt         # Python dependencies
├── video_classifications.csv # Generated results (created when first run)
└── README.md               # This file
```

## Features in Detail

### AI Classification System

- **Primary Model**: Qwen2.5-VL 7B for high-quality vision-language analysis
- **Fallback Model**: Gemma2 2B for faster processing when primary model is slow
- **Timeout Management**: Automatically increases timeout periods if models are struggling
- **Continuous Retry**: Keeps trying until successful or user cancels

### Data Extraction

- **Video Metadata**: Title, URL, duration, upload date
- **Channel Information**: Name and link to channel
- **Thumbnail Capture**: Screenshots saved as base64 in CSV
- **Playlist Context**: Source playlist name and URL

### Browser Automation

- **Multiple Chrome Paths**: Automatically finds Chrome/Chromium installation
- **WebDriver Management**: Handles chromedriver setup and fallbacks
- **Robust Selectors**: Multiple CSS selectors for reliable element finding
- **Error Recovery**: Graceful handling of UI changes and loading delays

### User Experience

- **Rich Console Output**: Colored logging with emojis and status indicators
- **Progress Tracking**: Clear indication of current processing status
- **Safe Exit**: Press 'q' at any time to cleanly stop processing
- **Error Reporting**: Detailed error messages for troubleshooting

## Testing Your Setup

Before running the main script, you can test individual components:

1. **Test Ollama Connection**:

   ```python
   import requests
   response = requests.get('http://localhost:11434/api/tags')
   print(response.json())
   ```

2. **Test Browser Automation**:
   Run the script and check if Chrome opens correctly

3. **Test Model Response**:
   The script will verify model availability on startup

## Troubleshooting 🔧

### Common Issues

**Ollama Connection Error**:

- Ensure Ollama is running: `ollama serve`
- Check the host URL in config.ini
- Verify models are installed: `ollama list`

**Browser Issues**:

- Install Chrome or Chromium
- Update chromedriver if needed
- Check if browser is in PATH

**Model Timeout**:

- The script automatically handles timeouts with fallback
- Consider increasing timeout values in config.ini
- Ensure sufficient system resources

**Selenium Errors**:

- YouTube may have changed their HTML structure
- Check for browser updates
- Verify you're logged into YouTube

### Performance Tips

- **For faster processing**: Use smaller models like `gemma2:2b` as primary
- **For better accuracy**: Use larger models like `qwen2.5vl:7b` as primary
- **For stability**: Keep both models installed for automatic fallback
- **For large playlists**: Consider running in smaller batches

## Contributing

1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly
4. Submit a pull request

## License

MIT License - see LICENSE file for details

---

**Note**: This tool is for personal use and educational purposes. Please respect YouTube's Terms of Service and rate limits.
