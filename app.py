"""
Meeting Notes Summarizer using Ollama
Requires: pip install flask flask-cors ollama
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
import json
import re

app = Flask(__name__)
CORS(app)

# Configuration
OLLAMA_MODEL = "llama3.2"  # or "mistral", "phi3", etc.

def create_analysis_prompt(transcript):
    """Create a structured prompt for the LLM"""
    return f"""You are a meeting analysis assistant. Analyze this transcript and extract key information.

Meeting Transcript:
{transcript}

CRITICAL: Return ONLY valid JSON. No markdown, no explanations, no code blocks. Just the JSON object.

Required JSON structure:
{{
    "meeting_summary": "2-3 sentence summary here",
    "participants": ["Name1", "Name2"],
    "key_decisions": [
        "Decision 1 text here",
        "Decision 2 text here"
    ],
    "action_items": [
        "Action item 1 with owner and deadline",
        "Action item 2 with owner and deadline"
    ],
    "discussion_points": [
        "Discussion point 1",
        "Discussion point 2"
    ]
}}

Rules:
- Each array item must be a SEPARATE string, not concatenated
- Extract 3-6 key decisions (major choices made)
- Extract 3-6 action items (tasks with owners/deadlines)
- Extract 4-8 discussion points (topics covered)
- Keep each item to 1-2 sentences maximum
- List all participant names
- Return ONLY the JSON object, nothing else"""

def extract_json_from_response(response_text):
    """Extract JSON from LLM response, handling various formats"""

    # Remove markdown code blocks if present
    cleaned = response_text.strip()
    if cleaned.startswith('```'):
        # Remove code block markers
        lines = cleaned.split('\n')
        if lines[0].startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].startswith('```'):
            lines = lines[:-1]
        cleaned = '\n'.join(lines)

    # Try to find JSON object in the response
    json_match = re.search(r'\{[\s\S]*\}', cleaned)
    if json_match:
        try:
            parsed = json.loads(json_match.group())

            # Ensure all required keys exist
            required_keys = ['meeting_summary', 'participants', 'key_decisions', 'action_items', 'discussion_points']
            for key in required_keys:
                if key not in parsed:
                    parsed[key] = [] if key != 'meeting_summary' else 'No summary available'

            # Post-process to split concatenated items
            for key in ['key_decisions', 'action_items', 'discussion_points']:
                if key in parsed and parsed[key]:
                    cleaned_items = []
                    for item in parsed[key]:
                        if isinstance(item, str):
                            # If item contains multiple bullet points, split them
                            if ' - ' in item and item.count(' - ') > 2:
                                split_items = [s.strip() for s in item.split(' - ') if s.strip()]
                                cleaned_items.extend(split_items)
                            else:
                                cleaned_items.append(item.strip())
                        else:
                            cleaned_items.append(str(item))
                    parsed[key] = cleaned_items

            return parsed
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Attempted to parse: {json_match.group()[:200]}")

    # Fallback: create structured response from text
    return {
        "key_decisions": ["Unable to parse LLM response - JSON format error"],
        "action_items": ["Try analyzing again or use a different model"],
        "discussion_points": ["Raw response: " + response_text[:300] + "..."],
        "participants": [],
        "meeting_summary": "Error: Could not parse the LLM response into structured format"
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if Ollama is running and model is available"""
    try:
        # Try to list models with better error handling
        models_response = ollama.list()

        # Handle different response formats
        if isinstance(models_response, dict):
            models_list = models_response.get('models', [])
        else:
            models_list = []

        # Extract model names safely
        model_names = []
        for model in models_list:
            if isinstance(model, dict):
                # Try different possible keys
                name = model.get('name') or model.get('model') or model.get('id')
                if name:
                    model_names.append(name)
            elif isinstance(model, str):
                model_names.append(model)

        return jsonify({
            'status': 'healthy',
            'ollama_running': True,
            'available_models': model_names,
            'current_model': OLLAMA_MODEL,
            'models_count': len(model_names)
        })
    except ConnectionError as e:
        return jsonify({
            'status': 'error',
            'ollama_running': False,
            'error': 'Cannot connect to Ollama. Make sure Ollama is running (ollama serve)',
            'details': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'ollama_running': False,
            'error': f'Ollama error: {str(e)}',
            'suggestion': 'Run: ollama list (to check if Ollama is working)'
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_meeting():
    """Analyze meeting transcript using Ollama"""
    try:
        data = request.json
        transcript = data.get('transcript', '')

        if not transcript.strip():
            return jsonify({'error': 'Empty transcript'}), 400

        # Create prompt
        prompt = create_analysis_prompt(transcript)

        # Call Ollama with stricter parameters for JSON output
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{
                'role': 'user',
                'content': prompt
            }],
            format='json',  # Force JSON output mode
            options={
                'temperature': 0.1,  # Very low temperature for consistent structured output
                'top_p': 0.9
            }
        )

        # Extract response
        response_text = response['message']['content']

        # Parse JSON from response
        analysis = extract_json_from_response(response_text)

        return jsonify({
            'success': True,
            'analysis': analysis,
            'model_used': OLLAMA_MODEL,
            'raw_response': response_text  # For debugging
        })

    except ConnectionError as e:
        return jsonify({
            'error': 'Cannot connect to Ollama',
            'suggestion': 'Make sure Ollama is running: ollama serve',
            'details': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'error': f'Error: {str(e)}',
            'suggestion': f'Make sure model is available: ollama pull {OLLAMA_MODEL}'
        }), 500

@app.route('/api/models', methods=['GET'])
def list_models():
    """List available Ollama models"""
    try:
        models_response = ollama.list()

        # Handle response safely
        if isinstance(models_response, dict):
            models_list = models_response.get('models', [])
        else:
            models_list = []

        model_names = []
        for model in models_list:
            if isinstance(model, dict):
                name = model.get('name') or model.get('model') or model.get('id')
                if name:
                    model_names.append(name)
            elif isinstance(model, str):
                model_names.append(model)

        return jsonify({
            'models': model_names
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'models': []
        }), 500

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API info"""
    return jsonify({
        'message': 'Meeting Notes Summarizer API',
        'endpoints': {
            '/api/health': 'Check Ollama connection status',
            '/api/analyze': 'POST meeting transcript for analysis',
            '/api/models': 'List available models'
        },
        'instructions': 'Open index.html in your browser to use the application'
    })

if __name__ == '__main__':
    print("=" * 60)
    print("Meeting Notes Summarizer - Ollama Backend")
    print("=" * 60)
    print(f"\nUsing model: {OLLAMA_MODEL}")
    print("\nMake sure Ollama is running:")
    print("  1. Install: https://ollama.ai/download")
    print(f"  2. Pull model: ollama pull {OLLAMA_MODEL}")
    print("  3. Check if running: ollama list")
    print("  4. If not running: ollama serve")
    print("\nStarting Flask server...")
    print("API will be available at: http://127.0.0.1:5000")
    print("=" * 60)

    app.run(debug=True, port=5000)