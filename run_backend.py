from backend.api import app

if __name__ == '__main__':
    # threaded=True allows the server to handle multiple requests at the same time
    # (e.g., streaming video while also serving API requests for the log)
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)