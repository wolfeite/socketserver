from .test.web_send_single import web_single_send
from .test.web_send_all import web_all_send
from .test.gui_config import config_gui
from .test.web_config import config_web
from .test.web_recv import web_config_recv

def createTestApp(gui, tcp, web):

    config_gui(gui, tcp, web)
    config_web(gui, web)

    web_config_recv(gui, web)
    web_single_send(gui, web)
    web_all_send(gui, web)

    gui.timer.start(200)
