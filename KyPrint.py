import sys
import qdarktheme
import socketio
import StarTSPImage
from PIL import Image, ImageDraw, ImageFont
import time
import socket
import obsws_python as obs
import inspect

# 1. Import QApplication and all the required widgets
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QPushButton
app = QApplication([])

window = QWidget()
window.setWindowTitle("KyPrint v2")
window.setFixedSize(400, 200)

qdarktheme.setup_theme()


obsMsg = QLabel("<h4 style='color:white;'>Connecting to OBS....</h4>", parent=window)
obsMsg.move(60, 15)

button1 = QPushButton(window)
button1.setText("Handle Queue")
button1.move(64,64)



window.show()


def read_config_data():
    config_data = {}
    try:
        with open("config.txt", "r") as file:
            for line in file:
                key, value = line.strip().split(':', 1)
                config_data[key.strip()] = value.strip()
    except FileNotFoundError:
        pass
    return config_data


scene = ""
id = 0
obsactive = False

class Observer:
    def __init__(self):
        self._client = None  # Initialize to None
        self._is_connected = False  # Add a flag to track the connection status
        self.cl = None  # Initialize the 'cl' client to None


    def connect_to_obs(self,):
        global obsactive, id, scene
        if not self._is_connected:
            self.cl = obs.ReqClient(host='localhost', port=4455, password='kyprint', timeout=3)
            self._client = obs.EventClient(host='localhost', port=4455, password='kyprint')
            self._client.callback.register(self.on_current_program_scene_changed)
            self._is_connected = True
            print("Connected to OBS server")
            obsactive = True
            obsMsg.setText("OBS Connected")
            resp = self.cl.get_current_program_scene()
            scene = resp.current_program_scene_name ## INITAL SCENE FETCH
            try:
                idresp = self.cl.get_scene_item_id(scene_name=scene, source_name="Printer")
                id = idresp.scene_item_id
                obsMsg.setText("OBS Connected\nPrinter cam in scene!")
            except:
                obsMsg.setText("OBS Connected\nPrinter cam <b>not</b> in scene!")


    @property
    def event_identifier(self):
        return inspect.stack()[1].function

    def on_current_program_scene_changed(self, data):
        global scene, id
        scene = data.scene_name
        try:
            idresp = self.cl.get_scene_item_id(scene_name=scene, source_name="Printer")
            id = idresp.scene_item_id
            obsMsg.setText("OBS Connected\nPrinter cam in scene!")
            print("Found printer source in this scene!")
        except:
            obsMsg.setText("OBS Connected\nPrinter cam <b>not</b> in scene!")
            id = 0

    def handleCam(self):
        try:
            if id > 0:
                config_data = read_config_data() 
                timer = config_data.get("AlertTimer", 7)
                self.cl.set_scene_item_enabled(scene_name=scene, item_id=id, enabled=True)
                time.sleep(int(timer))
                self.cl.set_scene_item_enabled(scene_name=scene, item_id=id, enabled=False)
        except:
            print("Couldn't activate source 'Printer'.")

observer = Observer()

sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print('Connecting to OBS')
    observer.connect_to_obs()

def obsConnect():
    print("CLICK")

# BIND OBS BUTTON
button1.clicked.connect(obsConnect)


sys.exit(app.exec())
