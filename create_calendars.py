import sys
from googleapiclient import errors
from utils import authenticate, get_existing_calendars, get_data


# not in use
def delete_all_calendars(service):
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if 'primary' not in calendar_list_entry or not calendar_list_entry['primary']:
                service.calendars().delete(calendarId=calendar_list_entry['id']).execute()
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break


def create_calendars_for_entities(entities, existing_calendars, service):
    for entity in entities:
        if entity not in [d['summary'] for d in existing_calendars]:
            calendar = {
                'summary': entity,
            }
            print("creating new calendar for " + str(entity))
            try:
                created_calendar = service.calendars().insert(body=calendar).execute()
                rule = {
                    'scope': {
                        'type': 'default',
                    },
                    'role': 'reader'
                }
                service.acl().insert(calendarId=created_calendar['id'], body=rule).execute()
            except errors.HttpError:
                print('quota limit')
                break


def main():
    service = authenticate(sys.argv)
    calendars = get_existing_calendars(service)
    _, entities = get_data()
    create_calendars_for_entities(entities, calendars, service)


if __name__ == '__main__':
    main()
