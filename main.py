from urllib.request import urlopen
import json
import sys
from oauth2client import client
from googleapiclient import sample_tools, errors
import dateutil.parser

url = "https://rfidis.raf.edu.rs/raspored/json.php"

day_to_date = {'PON': '13', 'UTO': '14', 'SRE': '15', 'CET': '16', '?ET': '16', 'PET': '17'}


def delete_all_calendars(argv):
    # Authenticate and construct service.
    service, flags = sample_tools.init(
        argv, 'calendar', 'v3', __doc__, __file__,
        scope='https://www.googleapis.com/auth/calendar')
    try:
        page_token = None
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                if 'primary' not in calendar_list_entry or not calendar_list_entry['primary']:
                    service.calendars().delete(calendarId=calendar_list_entry['id']).execute()
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
    except client.AccessTokenRefreshError:
        print('The credentials have been revoked or expired, please re-run the application to re-authorize.')


def delete_all_events(all_calendars, service):
    for c in all_calendars:
        events = get_existing_events(c['id'], service)
        for e in events:
            try:
                service.events().delete(calendarId=c['id'], eventId=e['id']).execute()
            except errors.HttpError:
                pass


def create_calendars_for_entities(entities, all_calendars, service):
    for entity in entities:
        if entity not in [d['summary'] for d in all_calendars]:
            calendar = {
                'summary': entity,
            }
            print("creating new calendar for " + str(entity))

            try:
                created_calendar = service.calendars().insert(body=calendar).execute()
                all_calendars.append(created_calendar)
            except errors.HttpError:
                print('quota limit')
                break

    return all_calendars


def get_existing_events(calendarId, service):
    event_list = []
    page_token = None
    while True:
        events = service.events().list(calendarId=calendarId, pageToken=page_token).execute()
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


def equal_timestamps(ts1, ts2):
    d1 = dateutil.parser.parse(ts1)
    d2 = dateutil.parser.parse(ts2)
    return d1 == d2 or abs((d1 - d2).hours) == 1


def main(argv):
    service = authenticate(argv)
    data, entities = get_data()

    all_calendars = get_existing_calendars(service)

    print('deleting existing events')
    delete_all_events(all_calendars, service)

    all_calendars = create_calendars_for_entities(entities, all_calendars, service)

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
            }
        }
        interested_entities = entry['nastavnik'] + [entry['ucionica']] + entry['grupe']
        for entity in interested_entities:
            if entity not in calendar_ids:
                continue
            cal_id = calendar_ids[entity]
            print(calendar_event)
            service.events().insert(calendarId=cal_id, body=calendar_event).execute()


if __name__ == '__main__':
    main(sys.argv)
