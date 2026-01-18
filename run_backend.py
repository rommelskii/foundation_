from backend.app import create_app
from backend.app.utils.env_helper import EnvVars

envs = EnvVars()
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=envs.API_PORT)
