#!/usr/bin/python
import math
import datetime
import statistics
import warnings
import calendar_helper_functions as icalhelper
import datetime
from session import Session
from atom import Atom

__TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
max_dist_between_logs = 15  # in minutes TODO these should be arguments for different types of input.
min_session_size = 15  # in minutes


def sleep_report(project_sessions):
        wake_list = [session.end for session in project_sessions]
        length_list=[session.length() for session in project_sessions]
        bed_list=[session.start for session in project_sessions]
        print(("Mean Sleep Length: {}".format(avg_length(length_list))))
        print(("Mean Bed Time: {}".format(avg_bed_time(bed_list))))
        print(("Mean Wake Time: {}".format(avg_wake_time(wake_list))))


def avg_bed_time(datetimes):
    total = datetime.timedelta()
    count = 0
    for dt in datetimes:
        if dt.time() >= datetime.time(20):
            total += datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second, microseconds=dt.microsecond)
            count += 1
    if count == 0:
        return None
    avg_seconds = round(total.total_seconds() / count)
    avg_time = datetime.datetime.min + datetime.timedelta(seconds=avg_seconds)
    return avg_time.time()


def avg_wake_time(datetimes):
    total = datetime.timedelta()
    count = 0
    for dt in datetimes:
        if dt.time() <= datetime.time(8):
            total += datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second, microseconds=dt.microsecond)
            count += 1
    if count == 0:
        return None
    avg_seconds = round(total.total_seconds() / count)
    avg_time = datetime.datetime.min + datetime.timedelta(seconds=avg_seconds)
    return avg_time.time()






def avg_length(time_deltas):
    IGNORE_DURATION = datetime.timedelta(hours=10) #Sleep longer than this is a tracking error 
    filtered_time_deltas = [td for td in time_deltas if td < IGNORE_DURATION]
    seconds = round(statistics.mean(td.total_seconds() for td in filtered_time_deltas))
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)



def days_old(session):
    delta = datetime.datetime.now() - session.start.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
    return delta.days

def get_sessions(atoms):
#This has two phases
        if len(atoms)==0:
            return []
        last= datetime.datetime.strptime( "2011-07-10 10:00:00", __TIME_FORMAT)
        lasttitle=atoms[0].title
        current = atoms[0].get_S()
        grouped_timevalues=[]
        current_group=[]
    #Step1: group all atoms into the largest groups such that every start time but one is within 15 minutes of an end time of another
    #Oh- that's NOT*actually* what this does...this does 'within 15 minutes of the *last*'
        for current in atoms:
                #print("enter loop") 
                #print(current.get_S())
                #print(last)
                if ((current.get_S()-last) > datetime.timedelta( minutes=max_dist_between_logs)):
                    grouped_timevalues.append(current_group)
                    current_group=[current]
                elif (current.get_S() <last): #preventing negative times being approved...
                    grouped_timevalues.append(current_group)
                    current_group=[current]
                elif (current.title != lasttitle): #preventing negative times being approved...
                    grouped_timevalues.append(current_group)
                    current_group=[current]
                last = current.get_E()
                lasttitle=current.title
                current_group.append(current)
        grouped_timevalues.append(current_group)
        #Step 2 - return those groups that are bigger than a set value.
        sessions=[]
        for i in grouped_timevalues:
            if i:
                if ((get_latest_end(i)-get_earliest_start(i)) >datetime.timedelta(minutes=min_session_size)):
                    sessions.append(Session(i[0].title,get_earliest_start(i),get_latest_end(i),i))
        return sessions

def get_latest_end(atoms):
    max=atoms[0].get_E()
    for atom in atoms:
        if atom.get_E()>max:
            max=atom.get_E()
    return max

def get_earliest_start(atoms):
    min=atoms[0].get_S()
    for atom in atoms:
        if atom.get_S()<min:
            min=atom.get_E()
    return min

def make_sleep_file(atoms):
     global max_dist_between_logs
     global min_session_size
     pre=max_dist_between_logs
     pre2=min_session_size
     min_session_size = 60  # in minutes
     max_dist_between_logs=240
     sessions=get_sessions(atoms)
     sessions=invert_sessions(sessions)
     max_dist_between_logs=pre
     min_session_size = pre2
     return sessions

def invert_sessions(sessions):
    lastsession=sessions[0]
    new_sessions=[]
    for session in sessions:
        new_sessions.append(Session(session.project,lastsession.end,session.start,session.content))
        lastsession=session
    return new_sessions

def heartrate_to_atoms(filename):
    #Incoming data is in this format: 
    # 2024-04-12 06:38:29,88.000
    timestamplength=len("2024-04-12 06:38:29")
    datelength=len("2024-04-12")
    content=icalhelper.get_content(filename)
    atoms=[]
    for a in content:
        start=a[datelength+1:timestamplength]
        date=a[:datelength]
        end=a[datelength+1:timestamplength]
       # print("{}, {}, {}".format(start,date,end))
        atoms.append(Atom(start,end,date,"Sleep","Alive",__TIME_FORMAT))#labeling it sleep is wrong, but it keep the same name for the inversion.
    atoms.pop(0)
    return atoms

def full_detect():
    watch_atoms=heartrate_to_atoms("/Users/ppac065/Downloads/Export.csv")
    print("All atoms created") 
    sleep_sessions=make_sleep_file(watch_atoms)
    for session in sleep_sessions:
        print(session)
    start_date = datetime.datetime.strptime("20-05-2024", "%d-%m-%Y")

    # Get the current date
    current_date = datetime.datetime.now()

    # Calculate the difference in days
    days_difference = (current_date - start_date).days


    segment_report(sleep_sessions,days_difference)
    segment_report(sleep_sessions,0)
    segment_report(sleep_sessions,365)
    segment_report(sleep_sessions,60)
    segment_report(sleep_sessions,30)
    segment_report(sleep_sessions,7)

def segment_report(sleep_sessions,days=0):
    sessions=[]
    if days==0:
        sessions=sleep_sessions
        days="all"
    else:
        sessions = [i for i in sleep_sessions if days_old(i)<days]
    print("## Last {} Days".format(days)) 
    sleep_report(sessions)

