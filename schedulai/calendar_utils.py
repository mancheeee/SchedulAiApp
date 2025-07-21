from auth import get_calendar_service
import datetime


def check_availability():
    service = get_calendar_service()
    now = datetime.datetime.utcnow().isoformat() + "Z"
    later = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat() + "Z"

    body = {"timeMin": now, "timeMax": later, "items": [{"id": "primary"}]}

    eventsResult = service.freebusy().query(body=body).execute()
    busy_times = eventsResult["calendars"]["primary"]["busy"]

    print("Busy slots:")
    for time in busy_times:
        print(f"From {time['start']} to {time['end']}")


def insert_test_event():
    service = get_calendar_service()
    event = {
        "summary": "Test Meeting with Sally",
        "start": {
            "dateTime": "2025-06-19T15:00:00",
            "timeZone": "Asia/Karachi",
        },
        "end": {
            "dateTime": "2025-06-19T16:00:00",
            "timeZone": "whatever your timezone is",  # change this accordingly
        },
    }

    event = service.events().insert(calendarId="primary", body=event).execute()
    print(f"Event created: {event.get('htmlLink')}")
