#!/usr/bin/env python3
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.get('/health')
def health():
    return jsonify({"status": "ok", "service": "heatlh_checker_backend"}), 200

@app.get('/health/deep')
def deep_health():
    return jsonify({
        "status": "ok",
        "checks": {
            "python": os.sys.version.split()[0],
            "cwd": os.getcwd()
        }
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
