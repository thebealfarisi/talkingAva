from flask import Flask, request, Response, send_from_directory, jsonify
import json

app = Flask(__name__, static_folder='public')

# Store received data
received_data = []

# Endpoint to receive JSON data
@app.route('/send-data', methods=['POST'])
def send_data():
    if not request.is_json:
        return jsonify({"error": "Invalid data format"}), 400
    
    json_data = request.get_json()
    # userid = json_data.get('userid')
    # query = json_data.get('query')
    print('Masuk 1')

    # if isinstance(userid, int) and isinstance(query, str):
    if json_data is not None:
        # Add the received data to the list
        received_data.append(json_data)
        return jsonify({"message": "Data received successfully"}), 200
    else:
        return jsonify({"error": "Invalid data format"}), 400

# SSE endpoint to stream data to the client
@app.route('/data-stream')
def data_stream():
    print('Masuk data_stream')
    def stream():
        print('Masuk stream')
        last_id = len(received_data)
        while True:
            if len(received_data) > last_id:
                data = received_data[last_id]
                last_id += 1
                yield f'data: {json.dumps(data)}\n\n'
    
    return Response(stream(), content_type='text/event-stream', headers={'Cache-Control': 'no-cache', 'Connection': 'keep-alive'})

# Endpoint to serve index.html
@app.route('/streamAva')
def stream_ava():
    return send_from_directory(app.static_folder, 'index-did.html')

# Serve static files
@app.route('/<path:filename>')
def serve_static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(port=3000, debug=True)