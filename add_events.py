import sys
from oauth2client import client
from googleapiclient import sample_tools, errors
from bs4 import BeautifulSoup
from utils import authenticate, get_existing_calendars, get_entities, get_data, get_entities_by_type

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


def create_index_page(all_calendars, entities_by_type):
    html = open("template.html", "r").read()
    soup = BeautifulSoup(html, 'html5lib')

    sorted_calendars = sorted([(c['id'], c['summary']) for c in all_calendars], key=lambda tup: tup[1])
    for calendar_id, calendar_summary in sorted_calendars:
        new_checkbox = BeautifulSoup(
            '<input type="checkbox" name="chkbx" value="' + calendar_id + '" onchange="changeCalendar()" >' +
            calendar_summary + '<br>', 'html5lib')
        summary = calendar_summary
        if summary in entities_by_type['classrooms']:
            soup.find('div', id="classroom_checkboxes").append(new_checkbox)
        elif summary in entities_by_type['lecturers']:
            soup.find('div', id="lecturer_checkboxes").append(new_checkbox)
        elif summary in entities_by_type['groups']:
            soup.find('div', id="group_checkboxes").append(new_checkbox)
        elif summary in entities_by_type['classes']:
            soup.find('div', id="class_checkboxes").append(new_checkbox)

    f = open('index.html', 'w')
    f.write(str(soup))
    f.close()


def main():
    service = authenticate(sys.argv)
    data = get_data()

    all_calendars = get_existing_calendars(service)
    delete_all_events(all_calendars, service)

    create_index_page(all_calendars, get_entities_by_type())

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
        interested_entities = entry['nastavnik'] + [entry['ucionica']] + entry['grupe'] + [entry['predmet']]
        for entity in interested_entities:
            if entity not in calendar_ids:
                continue
            cal_id = calendar_ids[entity]
            print(calendar_event)
            service.events().insert(calendarId=cal_id, body=calendar_event).execute()


if __name__ == '__main__':
    main()

