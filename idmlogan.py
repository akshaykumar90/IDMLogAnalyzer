import getopt
import sqlite3
import matplotlib.dates as mpldates
import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter
from matplotlib.dates import MONDAY
import datetime
import sys

class SqliteInterface:
    def __init__(self, db_filename, timescale, category, **kwargs):
        self.db_filename = db_filename
        self.timescale = timescale
        self.category = category
        if self.timescale != "all":
            self.period = kwargs['period']

    def __SQLScriptGenerator(self, category=False, start_date=False, end_date=False, sum=True):
        script_list = []
        script_list.append("SELECT date,")
        if sum:
            script_list.append("SUM(filesize) AS fs")
        else:
            script_list.append("filesize AS fs")
        script_list.append("FROM download")
        if start_date or end_date or category:
            script_list.append("WHERE")
            where_clause = []
            if start_date:
                where_clause.append("date > ?")
            if end_date:
                where_clause.append("date < ?")
            if category:
                where_clause.append("category = ?")
            script_list.append(' AND '.join(where_clause))
        if sum:
            script_list.append("GROUP BY date")
        script_list.append("ORDER BY")
        order_clause = []
        order_clause.append("date")
        if not sum:
            order_clause.append("time")
        script_list.append(','.join(order_clause))
        return " ".join(script_list)

    def __getDateValues(self, format, start, delta=1):
        if format == "year":
            y = int(start)
            start_date = "%d-01-01" % (y,)
            end_date = "%d-01-01" % (y+delta,)
        elif format == "month":
            month, year = start.split("/")
            m = int(month)
            y = int(year)
            start_date = "%d-%02d-01" % (y, m)
            m = m + delta
            y = y + (m / 12)
            end_date = "%d-%02d-01" % (y, m)
        elif format == "week":
            start_date_obj = datetime.datetime.strptime(start, "%m-%d-%Y")
            one_week = datetime.timedelta(days=7*delta)
            end_time_obj = start_date_obj + one_week
            start_date = start_date_obj.strftime("%Y-%m-%d")
            end_date = end_time_obj.strftime("%Y-%m-%d")

        return (start_date, end_date)
        
    def getXY(self):
        conn = sqlite3.connect(self.db_filename)
        cursor = conn.cursor()
        
        start_date_req = False
        end_date_req = False
        category_req = False
        
        parameter_list = []
        
        if self.timescale != "all":
            start_date_req = True
            end_date_req = True
            start_date, end_date = __getDateValues(self.timescale, self.period, delta=1)
            parameter_list.extend([start_date, end_date])
            
        if self.category != "all":
            category_req = True
            parameter_list.append(self.category)
            
        query = self.__SQLScriptGenerator(category_req, start_date_req, end_date_req)
        cursor.execute(query, tuple(parameter_list))
        
        data_all = [(date, value) for (date, value) in cursor.fetchall()]
        
        conn.close()
        
        fmtstring = "%Y-%m-%d"

        x = [mpldates.date2num(datetime.datetime.strptime(date, fmtstring)) for (date,value) in data_all]
        y = [value for (date,value) in data_all]
        
        return (x,y)

class LineChart:
    def __init__(self, timescale):
        self.timescale = timescale
    
    def draw(self):
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

class Controller:
    def __init__(self, chart_type, data_model, **kwargs):
        self.chart_type = chart_type
        self.data_model = data_model
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

# if __name__=="__main__": main(sys.argv[1:])
