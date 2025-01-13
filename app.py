from Flask import Flask, render_template, request, jsonify, Response
import requests
import json

app = Flask(__name__)

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    user_prompt = data.get('prompt') if data else None
    if not user_prompt:
        return jsonify({"error": "Prompt is required"}), 400

    payload = {
        "model" : MODEL_NAME,
        "prompt": f"Answer as an Economist {user_prompt}"
    }    
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, headers=headers, stream=True)
        response.raise_for_status()

        def stream_response():
            for line in response.iter_lines():
                if line:
                    try:
                        data = line.decoder("utf-8")
                        data_json = json.loads(data)
                        if "response" in data_json:
                            yield data_json["response"]
                        if data_json.get("done", False):
                            break
                    
                    except json.JSONDecodeError:
                        yield "Error decoding response"

        return Response(stream_response(), content_type='text/plain; charset=utf-8')
    
    except resquests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)