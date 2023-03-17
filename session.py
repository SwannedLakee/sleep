import datetime

class Session:
    project: str = "Unknown"
    start: datetime.datetime = None
    end: datetime.datetime = None
    content: str = ""

    def __init__(self, project: str, start: datetime.datetime, end: datetime.datetime, content: str = ""):
        if not isinstance(start, datetime.datetime):
            raise ValueError("Start must be a datetime.datetime object")
        if not isinstance(end, datetime.datetime):
            raise ValueError("End must be a datetime.datetime object")
        self.project = project
        self.start = start
        self.end = end
        self.content = content

    def length(self) -> datetime.timedelta:
        return (self.end - self.start)

    def __str__(self) -> str:
        return f"    {self.start.strftime('%a %d/%m/%y %H:%M')} to {self.end.strftime('%H:%M')} ({str(self.length())[:-3]})"

    @property
    def start(self) -> datetime.datetime:
        return self._start

    @start.setter
    def start(self, value: datetime.datetime):
        if not isinstance(value, datetime.datetime):
            raise ValueError("Start must be a datetime.datetime object")
        self._start = value

    @property
    def end(self) -> datetime.datetime:
        return self._end

    @end.setter
    def end(self, value: datetime.datetime):
        if not isinstance(value, datetime.datetime):
            raise ValueError("End must be a datetime.datetime object")
        self._end = value

    def __repr__(self) -> str:
        return f"Session(project='{self.project}', start='{self.start}', end='{self.end}', content='{self.content}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Session):
            return False
        return (self.project, self.start, self.end, self.content) == (other.project, other.start, other.end, other.content)





