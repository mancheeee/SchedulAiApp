import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QTextBrowser,
)
from auth import get_calendar_service
from calendar_api import (
    check_availability,
    create_event,
    create_test_event,
    is_slot_available,
    find_next_available_slot,
)
from gpt_parser import parse_user_input
from googleapiclient.errors import HttpError


class SchedulerBotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scheduler Chatbot")
        self.setGeometry(100, 100, 500, 400)

        self.layout = QVBoxLayout()
        self.chat_display = QTextBrowser()
        self.user_input = QLineEdit()
        self.send_button = QPushButton("Send")

        self.layout.addWidget(self.chat_display)
        self.layout.addWidget(self.user_input)
        self.layout.addWidget(self.send_button)
        self.setLayout(self.layout)

        self.send_button.clicked.connect(self.send_message)

        self.pending_event = None  # ⏳ Track confirmation step

        # Initialize Google Calendar service
        try:
            self.service = get_calendar_service()
            self.chat_display.append(
                "<b>Bot:</b> ✅ Google Calendar service connected."
            )
        except Exception as e:
            self.chat_display.append(f"<b>Bot:</b> ❌ Failed to connect: {str(e)}")
            self.service = None

    def send_message(self):
        text = self.user_input.text().strip()
        if not text:
            return

        self.chat_display.append(f"<b>You:</b> {text}")
        self.user_input.clear()

        if not self.service:
            self.chat_display.append("<b>Bot:</b> ❌ No calendar access.")
            return

        # Handle confirmation reply
        if self.pending_event:
            if "yes" in text.lower():
                title, datetime_str, attendees = self.pending_event
                try:
                    create_event(self.service, title, datetime_str, attendees)
                    self.chat_display.append(
                        f"<b>Bot:</b> ✅ Event created:<br><b>Title:</b> {title}<br><b>Time:</b> {datetime_str}<br><b>Attendees:</b> {', '.join(attendees)}"
                    )
                except HttpError as e:
                    self.chat_display.append(f"<b>Bot:</b> ❌ Calendar error: {e}")
                self.pending_event = None
            else:
                self.chat_display.append("<b>Bot:</b> ❎ Okay, event discarded.")
                self.pending_event = None
            return

        #  Commands
        if "free" in text.lower():
            self.chat_display.append("<b>Bot:</b> 🔍 Checking your calendar...")
            check_availability(self.service)
            self.chat_display.append(
                "<b>Bot:</b> ✅ Availability checked. See console."
            )
            return

        elif "test event" in text.lower():
            self.chat_display.append("<b>Bot:</b> 🧪 Creating test event...")
            create_test_event(self.service)
            self.chat_display.append("<b>Bot:</b> ✅ Test event created.")
            return

        # GPT Intent Parsing
        self.chat_display.append("<b>Bot:</b> 🤖 Thinking...")
        try:
            parsed = parse_user_input(text)
            if not parsed:
                self.chat_display.append("<b>Bot:</b> ❌ Couldn't understand that.")
                return

            title = parsed.get("title", "Untitled")
            datetime_str = parsed.get("datetime")
            attendees = parsed.get("attendees", [])

            if not datetime_str:
                self.chat_display.append("<b>Bot:</b> ❌ Missing date/time.")
                return

            # Check if the slot is free
            if not is_slot_available(self.service, datetime_str):
                alt_time = find_next_available_slot(self.service, datetime_str)
                self.chat_display.append(
                    f"<b>Bot:</b> ❗ You're busy at that time. How about <b>{alt_time}</b>? Try again with the new time."
                )
                return

            # Ask for confirmation
            self.chat_display.append(
                f"<b>Bot:</b> Do you want to schedule <b>{title}</b> at <b>{datetime_str}</b> with <b>{', '.join(attendees)}</b>? (yes/no)"
            )
            self.pending_event = (title, datetime_str, attendees)

        except Exception as e:
            self.chat_display.append(f"<b>Bot:</b> ❌ Unexpected error: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SchedulerBotApp()
    window.show()
    sys.exit(app.exec_())
