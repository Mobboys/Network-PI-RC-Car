import inputs
import websocket
import time
import json

ws = websocket.WebSocket()
ws.connect("ws://raspberrypi_ip:8080")

class XboxController:

  def read(self):
    # Use inputs to read controller values
    x = inputs.get_gamepad()[0].x
    y = inputs.get_gamepad()[0].y
    
    # Normalize between 0-1
    x = x / 32767 
    y = y / 32767
    
    return x, y
  

controller = XboxController() 

while True:
  x, y = controller.read()
  
  data = {
    'x': x,
    'y': y   
  }
  
  ws.send(json.dumps(data))
  time.sleep(0.01) # Send at 100Hz
