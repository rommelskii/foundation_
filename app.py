from flask import Flask, jsonify, request
from backend.env_helper import EnvVars 

app = Flask(__name__)
envs = EnvVars()

@app.route('/', methods=['GET']) 
def home():
    return jsonify({"message": f"Running on {envs.FLASK_APP}"}), 200

@app.route('/yolo', methods=['GET', 'POST'])
def yolo_frame_gen():
    """
    Perform a yolo inference      
    """
    

if __name__ == "__main__":
    app.run(debug=True, port=5050)
