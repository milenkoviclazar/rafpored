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
    return data


def get_entities():
    all_entities = get_entities_by_type()
    return all_entities['classrooms'] + all_entities['lecturers'] + all_entities['groups'] + all_entities['classes']


def get_entities_by_type():
    data = get_data()
    classrooms = []
    lecturers = []
    groups = []
    classes = []
    for entry in data:
        if entry['ucionica'] not in classrooms:
            classrooms.append(entry['ucionica'])
        if entry['predmet'] not in classes:
            classes.append(entry['predmet'])
        for lecturer in entry['nastavnik']:
            if lecturer not in lecturers:
                lecturers.append(lecturer)
        for group in entry['grupe']:
            if group not in groups:
                groups.append(group)
    return {'classrooms': sorted(classrooms), 'lecturers': sorted(lecturers),
            'groups': sorted(groups), 'classes': sorted(classes)}


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
