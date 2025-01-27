from PyQt5 import QtWidgets, uic
import sys
import zmq
from PyQt5.QtWidgets import QLabel, QInputDialog
from PyQt5.QtCore import QThread, pyqtSignal, Qt


# ZMQ Setup
context = zmq.Context()

# Socket to send messages to the server
sender = context.socket(zmq.PUSH)
sender.connect("tcp://192.168.0.113:5555") 

# Socket to receive messages from the server
receiver = context.socket(zmq.SUB)
receiver.connect("tcp://192.168.0.113:5556")  
receiver.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscribe to all messages


# Thread to listen for incoming messages
class MessageListener(QThread):
    message_received = pyqtSignal(str, str)  # Signal to emit (username, message, timestamp)

    def run(self):
        while True:
            # Receive message from the server
            message = receiver.recv_string()
            username, msg = message.split(":", 1)  # Split into username and message
            self.message_received.emit(username, msg)

class Ui(QtWidgets.QMainWindow):
    def __init__(self, username, *args, **kwargs):
        super(Ui, self).__init__(*args, **kwargs)
        uic.loadUi('main_window.ui', self)

        self.username = username
        self.setWindowTitle(f"Chat Window - {self.username}")

        self.chat_layout.setAlignment(Qt.AlignTop)

        self.message_input.returnPressed.connect(self.send_message)
        self.send_button.clicked.connect(self.send_message)

        # Start message listener thread
        self.listener = MessageListener()
        self.listener.message_received.connect(self.display_message)
        self.listener.start()

        self.show()

    def send_message(self):
        """Send a message to the server."""
        message = self.message_input.text()
        if message:
            full_message = f"{self.username}:{message}"  # Include username in the message
            sender.send_string(full_message)
            self.message_input.clear()

    def display_message(self, username, message):
        """Display a received message in the chat display."""
        bubble = QLabel()
        bubble.setTextFormat(Qt.RichText)
        bubble.setWordWrap(True)
        bubble.setStyleSheet("""
            QLabel {
                background-color: %s;
                color: %s;
                border-radius: 10px;
                padding: 8px;
                margin: 5px;
                max-width: 70%%;
            }
        """ % (
            "#DCF8C6" if username == self.username else "#FFFFFF",  # Bubble color
            "#000000" if username == self.username else "#000000"  # Text color
        ))

        # Align bubble to the right for sent messages, left for received messages
        if username == self.username:
            bubble.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        else:
            bubble.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Add message and timestamp
        bubble.setText(f"<b>{username}</b><br>{message}<br>")

        # Add bubble to chat layout
        self.chat_layout.addWidget(bubble)

        print(message)

        # Scroll to the bottom
        self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum())


app = QtWidgets.QApplication([])

# Get username from user input
username, ok = QInputDialog.getText(None, "Username", "Enter your username:")
if not ok or not username:
    sys.exit()

window = Ui(username)
app.exec_()