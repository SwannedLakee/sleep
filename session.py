class Session(object):
        project = "Unknown"
        start = ""
        end = ""
        content = ""

        def __init__(self, project, start, end, content):
                self.project, self.start, self.end = project, start, end

        def length(self):
                return (self.end-self.start)

        def __str__(self):
                return "    {} to {} ({})".format(
                    self.start.strftime("%d/%m/%y %H:%M"), self.end.strftime("%H:%M"), str(self.length())[:-3])


