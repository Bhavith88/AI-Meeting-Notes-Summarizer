# AI Meeting Notes Summarizer

A privacy-focused meeting transcript analyzer that uses local LLMs via Ollama. Extract key decisions, action items, and discussion points from meeting transcripts without sending data to the cloud.

## Overview

This application provides an intelligent meeting analysis system that:
- Processes meeting transcripts locally using Ollama
- Extracts structured information (decisions, action items, discussion points)
- Provides a clean web interface for easy interaction
- Ensures complete data privacy by keeping everything on your machine

## Features

- **Local Processing**: All data stays on your machine, no cloud services required
- **LLM-Powered Analysis**: Uses state-of-the-art language models (Llama 3.2, Mistral, etc.)
- **Intelligent Extraction**: Automatically identifies and categorizes meeting content
- **Web Interface**: Simple, intuitive UI for uploading transcripts and viewing results
- **File Support**: Accept text input directly or upload .txt files
- **Zero API Costs**: Unlimited usage with no recurring charges

## Technology Stack

- **Backend**: Python, Flask
- **AI Engine**: Ollama (local LLM inference)
- **Frontend**: HTML, CSS (Tailwind), JavaScript
- **Models**: Llama 3.2, Mistral, Phi-3, or any Ollama-compatible model

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running
- 8GB RAM minimum (16GB recommended for larger models)
- 5-10GB disk space for models

## Installation

### Step 1: Install Ollama

#### macOS and Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows
Download the installer from [https://ollama.ai/download](https://ollama.ai/download)

Verify installation:
```bash
ollama --version
```

### Step 2: Pull an LLM Model

Choose one of the following models based on your system resources:

```bash
# Recommended: Llama 3.2 (4.7GB)
ollama pull llama3.2

# Alternative: Mistral (4.1GB) - Fast and efficient
ollama pull mistral

# Alternative: Phi-3 (2.3GB) - Smaller, faster
ollama pull phi3

# Alternative: Llama 3.1 (8.5GB) - More powerful
ollama pull llama3.1
```

### Step 3: Set Up Python Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/meeting-summarizer.git
cd meeting-summarizer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install flask flask-cors ollama
```

### Step 4: Project Structure

Ensure your project has the following structure:
```
meeting-summarizer/
├── app.py              # Flask backend
├── index.html          # Frontend interface
├── README.md           # This file
└── venv/              # Virtual environment (created in Step 3)
```

## Usage

### Starting the Application

#### Terminal 1: Start Ollama Server (if not auto-started)
```bash
ollama serve
```

#### Terminal 2: Start Flask Backend
```bash
# Make sure virtual environment is activated
python app.py
```

You should see:
```
============================================================
Meeting Notes Summarizer - Ollama Backend
============================================================
Using model: llama3.2
Starting Flask server...
Running on http://127.0.0.1:5000
```

#### Terminal 3: Serve Frontend
```bash
# Option 1:
start index.html

# Option 2: Open index.html directly in your browser
# (May have CORS issues with some browsers)
```

Open your browser and navigate to `http://localhost:8000` (or open `index.html` directly).

### Using the Application

1. Verify the status indicator shows "Ollama Connected" (green)
2. Input your meeting transcript by either:
   - Pasting text directly into the text area
   - Uploading a .txt file using the "Upload .txt" button
3. Click "Analyze with AI"
4. Wait 10-30 seconds for processing
5. Review the extracted information organized into categories:
   - Meeting Summary
   - Participants
   - Key Decisions
   - Action Items
   - Discussion Points

## Sample Transcript

Use the sample transcript provided in the repository or use your own
```

## Configuration

### Changing the Model

Edit `app.py` and modify the model configuration:

```python
OLLAMA_MODEL = "mistral"  # Change to your preferred model
```

### Adjusting AI Parameters

Modify the Ollama chat parameters in `app.py`:

```python
options={
    'temperature': 0.1,  # Lower = more focused, Higher = more creative (0.0-1.0)
    'top_p': 0.9,        # Nucleus sampling parameter (0.0-1.0)
    'num_ctx': 4096      # Context window size
}
```

## API Endpoints

The Flask backend exposes the following endpoints:

- `GET /` - API information and documentation
- `GET /api/health` - Check Ollama connection status
- `POST /api/analyze` - Analyze meeting transcript
  - Request body: `{"transcript": "meeting text here"}`
  - Returns: Structured analysis with decisions, actions, and discussion points
- `GET /api/models` - List available Ollama models

## Troubleshooting

### "Cannot connect to Ollama"

Check if Ollama is running:
```bash
# Check process
ps aux | grep ollama  # macOS/Linux
tasklist | findstr ollama  # Windows

# Start Ollama if needed
ollama serve

# Test with a simple query
ollama run llama3.2 "Hello"
```

### "Model not found"

List and pull models:
```bash
# List installed models
ollama list

# Pull the required model
ollama pull llama3.2
```

### CORS Errors

- Ensure Flask backend is running on port 5000
- Verify `flask-cors` is installed: `pip install flask-cors`
- Try serving the frontend through an HTTP server instead of opening the file directly

### Slow Performance

- Use a smaller model: `ollama pull phi3`
- Reduce transcript length
- Close unnecessary applications to free up RAM
- Consider upgrading to a machine with more resources

### Parsing Errors

If the application shows "Unable to parse LLM response":
- The model may be returning invalid JSON
- Try using a different model (Llama 3.2 and Mistral work best)
- Check the raw response in the browser console for debugging
- Restart Ollama: `ollama serve`

## Model Comparison

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| phi3 | 2.3GB | Fast | Good | Quick testing, resource-constrained systems |
| mistral | 4.1GB | Fast | Great | Production use, balanced performance |
| llama3.2 | 4.7GB | Medium | Excellent | General purpose, recommended default |
| llama3.1 | 8.5GB | Slow | Excellent | Maximum accuracy, powerful systems |

## Development

### Project Structure

```
meeting-summarizer/
├── app.py              # Flask backend with API endpoints
│   ├── /api/health    # Health check endpoint
│   ├── /api/analyze   # Main analysis endpoint
│   └── /api/models    # List available models
├── index.html         # Frontend interface with UI logic
└── README.md          # Documentation
```

### Key Functions in app.py

- `create_analysis_prompt()` - Generates structured prompts for the LLM
- `extract_json_from_response()` - Parses and cleans LLM responses
- `health_check()` - Validates Ollama connection
- `analyze_meeting()` - Main analysis function

### Running in Development Mode

The Flask server runs in debug mode by default:
```python
app.run(debug=True, port=5000)
```

This enables:
- Auto-reload on code changes
- Detailed error messages
- Interactive debugger

**Important**: Never use debug mode in production environments.

## Production Deployment

For production deployment:

1. Disable debug mode in `app.py`:
```python
app.run(debug=False, port=5000)
```

2. Use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. Set up proper logging and error handling
4. Configure reverse proxy (Nginx, Apache)
5. Implement authentication if needed
6. Set up monitoring and health checks

## Future Enhancements

Potential features for future development:

- PDF export of meeting summaries
- Email integration for action item distribution
- Calendar integration for scheduling follow-ups
- Multi-language support
- Real-time meeting transcription integration
- Custom prompt templates for different meeting types
- User authentication and meeting history
- Team collaboration features
- Mobile application
- Integration with project management tools

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes with clear commit messages
4. Test thoroughly
5. Submit a pull request with a detailed description

## License

This project is available for internal use and demonstration purposes.

## Support

For issues, questions, or suggestions:

- Check the Troubleshooting section above
- Review Ollama documentation: [https://ollama.ai/docs](https://ollama.ai/docs)
- Open an issue on GitHub with detailed information about your problem

## Acknowledgments

- Built with Ollama for local LLM inference
- Uses Flask for the backend API
- Frontend styled with Tailwind CSS
- Supports multiple open-source language models

## System Requirements

**Minimum**:
- CPU: Dual-core processor
- RAM: 8GB
- Storage: 10GB free space
- OS: Windows 10+, macOS 10.15+, or Linux

**Recommended**:
- CPU: Quad-core processor or better
- RAM: 16GB
- Storage: 20GB free space (for multiple models)
- GPU: Optional but improves performance significantly

## Performance Benchmarks

Typical processing times (depends on transcript length and system):

- Short transcript (500 words): 10-15 seconds
- Medium transcript (1000 words): 15-25 seconds
- Long transcript (2000+ words): 25-40 seconds

Performance varies based on:
- Selected model size
- System resources
- Transcript complexity
- Concurrent system load

## Privacy and Security

This application prioritizes data privacy:

- All processing occurs locally on your machine
- No data is sent to external servers or APIs
- No internet connection required after initial model download
- Meeting transcripts are not stored or logged
- Suitable for confidential or sensitive meeting content

## Version History

**Version 1.0.0** (Current)
- Initial release
- Support for Ollama integration
- Basic meeting analysis features
- Web-based interface
- Multiple model support
