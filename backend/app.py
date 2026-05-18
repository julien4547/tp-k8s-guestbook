from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import os, socket, datetime, time

app = Flask(__name__)
MESSAGES = ["Bienvenue sur le livre d'or k8s !"]

REQUEST_COUNT = Counter('guestbook_requests_total', 'Nombre total de requetes', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('guestbook_request_seconds', 'Latence des requetes', ['endpoint'])

@app.route('/api/messages', methods=['GET', 'POST'])
def messages():
    start = time.time()
    REQUEST_COUNT.labels(method=request.method, endpoint='/api/messages').inc()
    if request.method == 'POST':
        data = request.get_json(force=True)
        MESSAGES.append(data.get('text', ''))
    resp = jsonify({'messages': MESSAGES, 'served_by': socket.gethostname(), 'env': os.environ.get('APP_ENV', 'dev'), 'ts': datetime.datetime.utcnow().isoformat()})
    REQUEST_LATENCY.labels(endpoint='/api/messages').observe(time.time() - start)
    return resp

@app.route('/api/health')
def health():
    REQUEST_COUNT.labels(method='GET', endpoint='/api/health').inc()
    return jsonify({'status': 'ok'}), 200

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
