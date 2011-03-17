import getopt
import sqlite3
import matplotlib.dates as mpldates
import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter
from matplotlib.dates import MONDAY
import datetime
import sys

class LineChart:
    def __init__(self, db, timescale, **kwargs):
        self.db_filename = db
        self.timescale = timescale
        if self.timescale != "all":
            self.period = kwargs['period']
    
    def draw(self):
        conn = sqlite3.connect(self.db_filename)
        cursor = conn.cursor()
        
        if self.timescale == "all":
            query = """SELECT date, SUM(filesize) AS fs FROM download GROUP BY date ORDER BY date"""
            cursor.execute(query)
        elif self.timescale == "month":
            month,year = self.period.split("/")
            m = int(month)
            y = int(year)
            start_date = "%d-%02d-01" % (y, m)
            m = m + 1
            if m > 12: y = y + 1
            end_date = "%d-%02d-01" % (y, m)
            query = """SELECT date, SUM(filesize) AS fs FROM download WHERE date > ? AND date < ? GROUP BY date ORDER BY date"""
            cursor.execute(query, (start_date, end_date))
        elif self.timescale == "year":
            year = self.period
            y = int(year)
            start_date = "%d-01-01" % (y,)
            end_date = "%d-01-01" % (y+1,)
            query = """SELECT date, SUM(filesize) AS fs FROM download WHERE date > ? AND date < ? GROUP BY date ORDER BY date"""
            cursor.execute(query, (start_date, end_date))
        
        data_all = [(date, value) for (date, value) in cursor.fetchall()]

        fmtstring = "%Y-%m-%d"

        x = [mpldates.date2num(datetime.datetime.strptime(date, fmtstring)) for (date,value) in data_all]
        y = [value for (date,value) in data_all]

        months = MonthLocator()
        monthsFmt = DateFormatter("%b '%y")
        weekFmt = DateFormatter("%m/%d")
        mondays = WeekdayLocator(MONDAY)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot_date(x,y,'-')
        
        if self.timescale == "all" or self.timescale == "year":
            ax.xaxis.set_major_locator(months)
            ax.xaxis.set_major_formatter(monthsFmt)
            ax.xaxis.set_minor_locator(mondays)
        else:
            ax.xaxis.set_major_formatter(weekFmt)
            ax.xaxis.set_major_locator(mondays)
        
        ax.autoscale_view()
        ax.grid(True)
        fig.autofmt_xdate()

        plt.show()
        
        conn.close()
    pass

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hlbpay:m:", ["help", "line", "bar", "pie", "all", "year=", "month="])
    except getopt.GetoptError:
        sys.exit(2)
    
    for opt,arg in opts:
        if opt in ("-l", "--line"):
            # Line Chart
            line = True
        elif opt in ("-b", "--bar"):
            # Bar Chart
            pass
        elif opt in ("-p", "--pie"):
            # Pie Chart
            pass
        elif opt in ("-a", "--all"):
            # Plot All Time data
            timescale = "all"
        elif opt in ("-m", "--month"):
            # Plot only for `arg` month
            timescale = "month"
            period = arg
        elif opt in ("-y", "--year"):
            # Plot only for `arg` year
            timescale = "year"
            period = arg
    
    if line:
        if timescale == "all":
            lc = LineChart("logan.db", timescale)
        else:
            lc = LineChart("logan.db", timescale, time=period)
        lc.draw()

if __name__=="__main__":
    main(sys.argv[1:])
