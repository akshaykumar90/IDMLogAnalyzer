import getopt
import sqlite3
import matplotlib.dates as mpldates
import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter
from matplotlib.dates import MONDAY
import datetime
import sys

class SqliteInterface:
    def __init__(self, db_filename, timescale='all', category='all', time_wise_grouping='no', \
                 category_wise_grouping=False, **kwargs):
        self.db_filename = db_filename
        self.timescale = timescale
        self.time_wise_grouping = time_wise_grouping
        self.category_wise_grouping = category_wise_grouping
        self.category = category
        if self.timescale != "all":
            self.period = kwargs['period']

    def __generateSQLScript(self, category=False, start_date=False, end_date=False, \
                            group_files=False, **kwargs):
        select_sql   = "SELECT"
        from_sql     = "FROM download"
        where_sql    = "WHERE"
        group_by_sql = "GROUP BY"
        order_by_sql = "ORDER BY"
        
        select_clause = []
        where_clause = []
        group_by_clause = []
        order_by_clause = []
        
        if group_files and kwargs.has_key('group_by'):
            grouping_element = kwargs['group_by']
        else:
            grouping_element = None
        
        if group_files:
            if grouping_element == 'date':
                select_clause.append('date')
                order_by_clause.append('date')
                group_by_clause.append('date')
            elif grouping_element == 'category':
                select_clause.append('category')
                group_by_clause.append('category')
                order_by_clause.append('category')
            else:
                pass
            select_clause.append('SUM(filesize) AS fs')
        else:
            select_clause.append('date')
            select_clause.append('time')
            select_clause.append('filesize AS fs')
            order_by_clause.append('date')
            order_by_clause.append('time')
        if start_date:
            where_clause.append('date > ?')
        if end_date:
            where_clause.append('date < ?')
        if category:
            where_clause.append('category = ?')
        
        if not where_clause: where_sql = ""
        if not group_by_clause: group_by_sql = ""
        if not order_by_clause: order_by_sql = ""
        
        return " ".join([select_sql, ",".join(select_clause),     \
                        from_sql,                                 \
                        where_sql, " AND ".join(where_clause),    \
                        group_by_sql, ",".join(group_by_clause),  \
                        order_by_sql, ",".join(order_by_clause)])

    def __getDateTuple(self, format, start, delta=1):
        if format == "year":
            y = int(start)
            start_date_str = "%d-01-01" % (y,)
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date_str = "%d-01-01" % (y+delta,)
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
        elif format == "month":
            month, year = start.split("/")
            m = int(month)
            y = int(year)
            start_date_str = "%d-%02d-01" % (y, m)
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
            m = m + delta
            y = y + (m / 12)
            end_date_str = "%d-%02d-01" % (y, m)
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
        elif format == "week":
            start_date = datetime.datetime.strptime(start, "%m-%d-%Y")
            one_week = datetime.timedelta(days=7*delta)
            end_time = start_date_obj + one_week

        return (start_date, end_date)
    
    def __getDateList(self, start_date, end_date, delta):
        date_list = []
        
        if delta == "month":
            n = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 2
            month = start_date.month
            year = start_date.year
            for i in range(n):
                date_list.append("%d-%02d-01" % (year, month))
                month = month + 1
                if (month > 12):
                    month = 1
                    year = year + 1
        elif delta == "year":
            n = end_date.year - start_date.year + 2
            year = start_date.year
            for i in range(n):
                date_list.append("%d-01-01" % (year,))
                year = year + 1
        
        return date_list
        
    def getData(self):
        conn = sqlite3.connect(self.db_filename)
        cursor = conn.cursor()
        
        if self.timescale != "all":
            timescale_lower, timescale_upper = self.__getDateTuple(self.timescale, self.period)
            if self.time_wise_grouping == "month" or self.time_wise_grouping == "year":
                date_list = self.__getDateList(timescale_lower, timescale_upper, self.time_wise_grouping)
                n_queries = len(date_list) - 1
            else:
                date_list = [ timescale_lower, timescale_upper ]
                n_queries = 1
        elif self.time_wise_grouping == "month" or self.time_wise_grouping == "year":
            cursor.execute("""SELECT date FROM download ORDER BY date LIMIT 1""")
            timescale_lower, = cursor.fetchone()
            cursor.execute("""SELECT date FROM download ORDER BY date DESC LIMIT 1""")
            timescale_upper, = cursor.fetchone()
            date_list = self.__getDateList(timescale_lower, timescale_upper, self.time_wise_grouping)
            n_queries = len(date_list) - 1
        else:
            date_list = None
            n_queries = 1
            
        if self.category == "all":
            category = False
        else:
            category = True
        
        if date_list:
            start_date = True
            end_date = True
        else:
            start_date = False
            end_date = False
        
        if self.time_wise_grouping == 'no':
            select_time = True
            group_by_category = False
            group_by_date = False
        elif self.time_wise_grouping == 'date':
            select_time = False
            group_by_date = True
            sum_filesize = True
        else:
            select_time = False
            group_by_date = False
            sum_filesize = True
        
        if self.category_wise_grouping:
            group_by_category = True
            group_by_date = False
        else:
            group_by_category = False
            group_by_date = False
        
        if self.time_wise_grouping == 'no' and self.timescale == 'week':
            group_by_date = False
            select_time = True
            
        conn.close()

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
