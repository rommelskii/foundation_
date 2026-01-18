from backend.app import create_app
from backend.app.utils.env_helper import EnvVars
from flask_cors import CORS

envs = EnvVars()
app = create_app()
CORS(app)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=envs.API_PORT)
