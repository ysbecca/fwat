from app import app

import socket

hostname = socket.gethostbyname(socket.gethostname())

app.run(host=hostname, port=5000, debug=True)
#app.run(debug=True)
