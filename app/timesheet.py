# Calendar string to parse example
data = "b'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//IDN nextcloud.com//Calendar app 2.0.2//EN\r\nCALSCALE:GREGORIAN\r\nBEGIN:VEVENT\r\nCREATED:20200330T134353Z\r\nDTSTAMP:20200330T134523Z\r\nLAST-MODIFIED:20200330T134523Z\r\nSEQUENCE:2\r\nUID:4a3ac2a2-16c0-4848-bd9e-7e137ed44b0e\r\nDTSTART;VALUE=DATE:20200331\r\nDTEND;VALUE=DATE:20200401\r\nSUMMARY:Malattia user 1\r\nATTENDEE;CN=danilo;CUTYPE=INDIVIDUAL;PARTSTAT=ACCEPTED;ROLE=REQ-PARTICIPANT\r\n ;SCHEDULE-STATUS=2.0:mailto:danilo.pacifico@gmail.com\r\nORGANIZER;CN=Isabella Fat:mailto:i.fat@quasarpm.com\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n'"
data2 = "b'BEGIN:VCALENDAR\r\nCALSCALE:GREGORIAN\r\nVERSION:2.0\r\nPRODID:-//Apple Inc.//Mac OS X 10.12.6//EN\r\nBEGIN:VEVENT\r\nCREATED:20200331T102807Z\r\nUID:963E05F7-4B43-434F-ADFF-6E45A14BDA86\r\nDTEND;TZID=Europe/Rome:20200402T100000\r\nTRANSP:OPAQUE\r\nX-APPLE-TRAVEL-ADVISORY-BEHAVIOR:AUTOMATIC\r\nSUMMARY:test caldav\r\nDTSTART;TZID=Europe/Rome:20200402T090000\r\nDTSTAMP:20200331T163243Z\r\nSEQUENCE:0\r\nCATEGORIES:Lavoro,Non in ufficio\r\nLAST-MODIFIED:20200331T163243Z\r\nEND:VEVENT\r\nBEGIN:VTIMEZONE\r\nTZID:Europe/Rome\r\nBEGIN:DAYLIGHT\r\nTZOFFSETFROM:+0100\r\nTZOFFSETTO:+0200\r\nTZNAME:CEST\r\nDTSTART:19700329T020000\r\nRRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU\r\nEND:DAYLIGHT\r\nBEGIN:STANDARD\r\nTZOFFSETFROM:+0200\r\nTZOFFSETTO:+0100\r\nTZNAME:CET\r\nDTSTART:19701025T030000\r\nRRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU\r\nEND:STANDARD\r\nEND:VTIMEZONE\r\nEND:VCALENDAR'"

datalist = data.split("\\r\\n")
from datetime import datetime
def event_parse(event_data):
    '''
    event = {
        'start_date':datetime.strptime(event_data.split('DTSTART')[1].split(':')[1].split('\r\n')[0],'%Y%m%dT%H%M%S'),
        'end_date': event_data.split('DTEND')[1].split(':')[1].split('\r\n')[0],
        'title': event_data.split('SUMMARY:')[1].split('\r\n')[0],
        #'organizer': event_data.split('ORGANIZER;CN=')[1].split(':')[0],
        #'attendee': event_data.split('ATTENDEE;CN=')[1].split(';')[0],
        #'attendee_status': event_data.split('PARTSTAT=')[1].split(';')[0],
    }
    '''
    event ={}
    event['title'] = event_data.split('SUMMARY:')[1].split('\r\n')[0]
    # all the day must referer to standard working hours (still hardcoded)
    s_start = 'T0900'
    s_end = 'T1800'

    start_date = event_data.split('DTSTART')[1].split(':')[1].split('\r\n')[0]
    end_date = event_data.split('DTEND')[1].split(':')[1].split('\r\n')[0]
    
    if len(start_date) < 10:
        start_date = start_date + s_start
        end_date = end_date + s_end

    start_date = datetime.strptime(start_date,'%Y%m%dT%H%M%S')
    end_date = datetime.strptime(end_date,'%Y%m%dT%H%M%S')
    delta = end_date-start_date
    event['delta_days'] = delta.days
    event['delta_hours'] = delta.seconds/3600
     
    # Organizator and attendees are there
    try:
        event['organizer'] = event_data.split('ORGANIZER;CN=')[1].split(':')[0]
        event['attendee']= event_data.split('ATTENDEE;CN=')[1].split(';')[0]
        event['attendee_status']= event_data.split('PARTSTAT=')[1].split(';')[0]
    except: pass
    return event

for f in datalist:

    print(f)

from sqlalchemy import create_engine


engine = create_engine('mysql://superset:300777Superset@cloud.quasarpm.com/nextcloud')
query = '''
SELECT 
    oc_calendarobjects.id as event_id,
    oc_calendars.id as calendar_id,
    oc_calendarobjects.calendardata as event_data,
    oc_calendarobjects.lastmodified as event_changed_on,
    oc_calendarobjects.etag as event_etag,
    oc_calendarobjects.firstoccurence as event_first_occurence,
    oc_calendarobjects.lastoccurence as event_last_occurence,
    oc_calendarobjects.classification as event_classification,
    oc_calendarobjects.calendartype as event_calendar_type,
    oc_calendars.principaluri as calendar_uri,
    oc_calendars.displayname as calendar_name,
    oc_calendars.description as calendar_description

FROM oc_calendarobjects
JOIN oc_calendars on oc_calendarobjects.calendarid = oc_calendars.id
WHERE oc_calendarobjects.componenttype = 'VEVENT'
'''

with engine.connect() as connection:
    result = connection.execute(query)
    for row in result:
        print('user:',row['calendar_uri'].rsplit('/')[-1],'cal:', row['calendar_name'])
        print(event_parse(row['event_data'].decode()))
        print('')
