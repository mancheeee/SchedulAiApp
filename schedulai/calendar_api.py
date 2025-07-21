from datetime import datetime, timedelta
from googleapiclient.errors import HttpError
import pytz


def check_availability(service):
    now = datetime.utcnow().isoformat() + "Z"
    later = (datetime.utcnow() + timedelta(hours=5)).isoformat() + "Z"

    events_result = (
        service.freebusy()
        .query(body={"timeMin": now, "timeMax": later, "items": [{"id": "primary"}]})
        .execute()
    )

    for item in events_result["calendars"]["primary"]["busy"]:
        print("⛔ Busy:", item)
    if not events_result["calendars"]["primary"]["busy"]:
        print("✅ You're free in the next 5 hours!")


def create_test_event(service):
    start = datetime.utcnow() + timedelta(minutes=5)
    end = start + timedelta(minutes=30)

    event = {
        "summary": "Schedulai Test Event",
        "start": {"dateTime": start.isoformat() + "Z"},
        "end": {"dateTime": end.isoformat() + "Z"},
    }

    event = service.events().insert(calendarId="primary", body=event).execute()
    print(f"✅ Test event created: {event.get('htmlLink')}")


def create_event(service, title, start_datetime, attendees):
    try:
        # Filter valid emails
        valid_attendees = [{"email": a} for a in attendees if "@" in a and "." in a]

        if not valid_attendees:
            print("⚠️ No valid emails found. Creating event without attendees.")

        event = {
            "summary": title,
            "start": {"dateTime": start_datetime, "timeZone": "Asia/Karachi"},
            "end": {
                "dateTime": (
                    datetime.fromisoformat(start_datetime) + timedelta(minutes=30)
                ).isoformat(),
                "timeZone": "Asia/Karachi",
            },
            "attendees": valid_attendees if valid_attendees else [],
        }

        print("📤 Sending event to Google Calendar:\n", event)

        created_event = (
            service.events().insert(calendarId="primary", body=event).execute()
        )
        print("✅ Event created:", created_event.get("htmlLink"))
        return created_event

    except Exception as e:
        print("❌ Calendar API error:", e)
        raise


def is_slot_available(service, start_str):
    try:
        # Convert string to datetime object
        local = pytz.timezone("Asia/Karachi")
        start = datetime.strptime(start_str, "%Y-%m-%dT%H:%M:%S")
        start_local = local.localize(start)

        end_local = start_local + timedelta(minutes=30)

        # Convert to UTC for Google Calendar API
        start_utc = start_local.astimezone(pytz.utc).isoformat()
        end_utc = end_local.astimezone(pytz.utc).isoformat()

        body = {
            "timeMin": start_utc,
            "timeMax": end_utc,
            "items": [{"id": "primary"}],
        }

        response = service.freebusy().query(body=body).execute()
        busy_times = response["calendars"]["primary"]["busy"]

        return len(busy_times) == 0

    except Exception as e:
        print("❌ Error checking slot availability:", e)
        return False


def find_next_available_slot(service, iso_datetime_str, attempts=10):
    """Find next free 30-min slot within next few hours."""
    base_time = datetime.fromisoformat(iso_datetime_str)

    for i in range(1, attempts + 1):
        new_time = base_time + timedelta(minutes=30 * i)
        if is_slot_available(service, new_time.isoformat()):
            return new_time.isoforma_
