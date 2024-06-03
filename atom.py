import datetime
m = { 'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12 }


def fastStrptime(val, format):
    #print("enter fast strptime {}".format(val)) 
# edited from http://ze.phyr.us/faster-strptime/
    try:
        l = len(val)
        if format == '%d/%m/%y %H:%M' and (l == 14):
            temp= datetime.datetime(
                2000+int(val[6:8]), # %Y
                int(val[3:5]), # %m
                int(val[0:2]), # %d
                int(val[9:11]), # %H
                int(val[12:14]), # %M
                0, # %s
                0, # %f
            )
            return temp
        # The watch
        if format == "%d-%b-%Y %H:%M" and (l == 17):
            temp= datetime.datetime(
                int(val[7:11]), # %Y
                m[val[3:6]], # %m
                int(val[0:2]), # %d
                int(val[12:14]), # %H
                int(val[15:17]), # %M
                0, # %s
                0, # %f
            )
            return temp
        # Default to the native strptime for other formats.
    #    print("Warning: falling through {}|{}|{}".format(val, format, l))
        return datetime.datetime.strptime(val, format)
    except ValueError:
        print("Exception for this:")
        print(val)
        print(format)
        raise ValueError

class Atom(object):

        def __init__(self, start="",end="", date="",title="", content="", TF="%Y-%m-%d %H:%M"):
            self.content=content
            self.start=start
            self.title=title
            self.end=end
            self.date=date
            self.TF=TF
            self.s=None
            self.e=None

        def get_S(self):
          try:
            total_date=self.date+" "+self.start
            if not self.s:
                self.s= fastStrptime(total_date,self.TF)
            return self.s
          except ValueError:
            print("Exception:")
            print(self)

        def get_E(self):
          try:
            total_date=self.date+" "+self.end
          #  print("get_E: Total date={}".format(total_date))
            if not self.e:
                self.e= fastStrptime(total_date,self.TF)
		
            types=str(type(self.e))
            if "date" not in types:
                self.e= fastStrptime(total_date,self.TF)
#                self.e= datetime.datetime.strptime(total_date,self.TF)
            #print self.e
            return self.e
          except ValueError:
            print("Exception in E:")
            print(self)

        def __str__(self):
            return "{}, from {} to {} on {}".format(self.title,self.start,self.end,self.date)


