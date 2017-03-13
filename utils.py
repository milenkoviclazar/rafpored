import json
from googleapiclient import sample_tools
from urllib.request import urlopen

url = "https://rfidis.raf.edu.rs/raspored/json.php"


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


def get_existing_calendars(service):
    calendars = []
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            calendars.append(calendar_list_entry)
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    return calendars


def authenticate(argv):
    service, flags = sample_tools.init(
        argv, 'calendar', 'v3', __doc__, __file__,
        scope='https://www.googleapis.com/auth/calendar')
    return service
