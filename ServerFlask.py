from websockets.server import WebSocketApp
import json

ws = WebSocketApp("0.0.0.0", 8080)

def on_message(ws, message):
  data = json.loads(message)
  
  x = data['x']
  y = data['y']
  
  # Control motors, servos, etc based on x, y
  
ws.on_message = on_message
ws.run_forever()
