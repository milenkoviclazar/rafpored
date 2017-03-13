from urllib.request import urlopen
import json
import sys
from oauth2client import client
from googleapiclient import sample_tools, errors
from bs4 import BeautifulSoup

url = "https://rfidis.raf.edu.rs/raspored/json.php"

day_to_date = {'PON': '6', 'UTO': '7', 'SRE': '8', 'CET': '9', '?ET': '9', 'PET': '10'}


def delete_all_events(all_calendars, service):
    print('deleting existing events')
    for c in all_calendars:
        events = get_existing_events(c['id'], service)
        for e in events:
            try:
                service.events().delete(calendarId=c['id'], eventId=e['id']).execute()
            except errors.HttpError:
                pass


def get_existing_events(calendar_id, service):
    event_list = []
    page_token = None
    while True:
        events = service.events().list(calendarId=calendar_id, pageToken=page_token).execute()
        for event in events['items']:
            event_list.append(event)
        page_token = events.get('nextPageToken')
        if not page_token:
            break
    return event_list


def get_existing_calendars(service):
    all_calendars = []
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            all_calendars.append(calendar_list_entry)
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    return all_calendars


def set_public_access(calendars, service):
    for calendar in calendars:
        rule = {
            'scope': {
                'type': 'default',
            },
            'role': 'reader'
        }
        service.acl().insert(calendarId=calendar['id'], body=rule).execute()


# download json page from url
def get_data():
    html = urlopen(url).read().decode('utf-8')
    data = json.loads(html)

    for entry in data:
        entry['grupe'] = [s.strip() for s in entry['grupe'].split(',')]
        entry['nastavnik'] = [s.strip() for s in entry['nastavnik'].split(',')]

    entities = []

    for entry in data:
        if entry['ucionica'] not in entities:
            entities.append(entry['ucionica'])
        for nastavnik in entry['nastavnik']:
            if nastavnik not in entities:
                entities.append(nastavnik)
        for grupa in entry['grupe']:
            if grupa not in entities:
                entities.append(grupa)

    return data, entities


def authenticate(argv):
    service, flags = sample_tools.init(
        argv, 'calendar', 'v3', __doc__, __file__,
        scope='https://www.googleapis.com/auth/calendar')
    return service


def create_index_page(all_calendars):
    html = open("template.html", "r").read()
    soup = BeautifulSoup(html, 'html.parser')
    for calendar in all_calendars:
        new_checkbox = BeautifulSoup(
            '<input type="checkbox" name="chkbx" value="' + calendar['id'] + '" onchange="changeCalendar()">' +
            calendar['summary'] + '<br>', 'html.parser')
        soup.find(id="checkboxes").append(new_checkbox)
    f = open('index.html', 'w')
    f.write(str(soup))
    f.close()


def main():

    service = authenticate(sys.argv)
    data, entities = get_data()

    all_calendars = get_existing_calendars(service)

    delete_all_events(all_calendars, service)

    all_calendars = create_calendars_for_entities(entities, all_calendars, service)

    create_index_page(all_calendars)

    set_public_access(all_calendars, service)
    calendar_ids = {}
    for cal in all_calendars:
        calendar_ids[cal['summary']] = cal['id']

    for entry in data:
        start_time, end_time = entry['termin'].split("-")
        if len(start_time) < 5:
            start_time = '0' + start_time
        start_time += ':00'
        if len(end_time) < 2:
            end_time = '0' + end_time
        end_time += ':00:00'
        calendar_event = {
            'summary': entry['predmet'] + ' (' + entry['tip'] + ')',
            'location': entry['ucionica'],
            'description': entry['tip'] + ' ' + str(entry['nastavnik']),
            'start': {
                'dateTime': '2017-03-' + day_to_date[entry['dan']] + 'T' + start_time,
                'timeZone': 'Europe/Belgrade'
            },
            'end': {
                'dateTime': '2017-03-' + day_to_date[entry['dan']] + 'T' + end_time,
                'timeZone': 'Europe/Belgrade'
            },
            "recurrence": [
                "RRULE:FREQ=WEEKLY;UNTIL=20170509T220000Z",
            ],
        }
        interested_entities = entry['nastavnik'] + [entry['ucionica']] + entry['grupe']
        for entity in interested_entities:
            if entity not in calendar_ids:
                continue
            cal_id = calendar_ids[entity]
            print(calendar_event)
            service.events().insert(calendarId=cal_id, body=calendar_event).execute()


if __name__ == '__main__':
    main()

