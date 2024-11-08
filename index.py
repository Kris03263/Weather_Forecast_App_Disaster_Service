from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_socketio import SocketIO
app = Flask(__name__)
socketio = SocketIO(app,async_mode='gevent')
api = Api(app)
CORS(app)
@app.route('/')
def index():
    return 'hello there2'
from DisasterControl.DisasterControl import disasterControl_blueprint,register_socketio_events
app.register_blueprint(disasterControl_blueprint, url_prefix='/Disaster')
register_socketio_events(socketio)

if __name__ == '__main__':
    socketio.run(app, host= "0.0.0.0", port=8080, debug=True, allow_unsafe_werkzeug=True,use_reloader=False)