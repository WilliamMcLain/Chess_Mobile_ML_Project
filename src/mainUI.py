# mainUI.py — run this to start everything
from flask import Flask, request, jsonify
from flask_cors import CORS
import pieces

app = Flask(__name__)
CORS(app)

@app.route('/move', methods=['POST'])
def make_move():
    data = request.json
    side  = data.get('side')
    piece = data.get('piece')
    start = data.get('start')
    end   = data.get('end')

    result = pieces.Pieces.prime(side, piece, start, end)
    return jsonify({'valid': result})

@app.route('/reset', methods=['POST'])
def reset():
    import csv_setup
    csv_setup.csv_setup.setup()
    return jsonify({'ok': True})

if __name__ == '__main__':
    print("Chess backend running on http://localhost:5000")
    app.run(debug=True, port=5000)