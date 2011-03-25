import sqlite3
import datetime

class SqliteInterface:
    def __init__(self, db_filename, timescale='all', category='all', time_wise_grouping='date', \
                 category_wise_grouping=False, **kwargs):
        self.categoryList = ['Compressed', 'Documents', 'General', 'Music', 'Programs', 'Video']
        
        self.db_filename = db_filename
        self.timescale = timescale
        self.time_wise_grouping = time_wise_grouping
        self.category_wise_grouping = category_wise_grouping
        self.category = category
        self.xvalues_as_datetime = False
        self.yvalues_as_list = False
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
            where_clause.append('date >= ?')
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
            end_date = start_date + one_week

        return (start_date, end_date)
    
    def __getDateList(self, start_date, end_date, delta, raw_dates=False):
        date_list = []
        
        if delta == "month":
            n = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
            if raw_dates:
                n = n + 1
            month = start_date.month
            year = start_date.year
            for i in range(n):
                date_list.append("%d-%02d-01" % (year, month))
                month = month + 1
                if (month > 12):
                    month = 1
                    year = year + 1
        elif delta == "year":
            n = end_date.year - start_date.year + 1
            if raw_dates:
                n = n + 1
            year = start_date.year
            for i in range(n):
                date_list.append("%d-01-01" % (year,))
                year = year + 1
        
        return date_list
    
    def strToDateTime(self, date_str_list, fmt=None):
        if fmt == None:
            fmt = "%Y-%m-%d"
        return [datetime.datetime.strptime(dt_str, fmt) for dt_str in date_str_list]
    
    def __getXRange(self, x_list, delta):
        date_list = self.strToDateTime(x_list)
        if delta == 'month':
            fmt = "%b '%y"
        elif delta == 'year':
            fmt = "%Y"
        return [dt_obj.strftime(fmt) for dt_obj in date_list[:-1]]
    
    def get_xvalues_type(self):
        return self.xvalues_as_datetime
    
    def get_yvalues_type(self):
        return self.yvalues_as_list
    
    def getData(self):
        conn = sqlite3.connect(self.db_filename)
        cursor = conn.cursor()
        
        # Defaults for __generateSQLScript
        category    = False
        start_date  = False
        end_date    = False
        group_files = False
        group_by    = None
        xvalues     = []
        yvalues     = []
        
        if self.timescale != "all":
            timescale_lower, timescale_upper = self.__getDateTuple(self.timescale, self.period)
            if self.time_wise_grouping == "month" or self.time_wise_grouping == "year":
                # Dataset No. 4
                date_list = self.__getDateList(timescale_lower, timescale_upper, self.time_wise_grouping)
                n_queries = len(date_list) - 1
                group_files = True
                xvalues = self.__getXRange(date_list, self.time_wise_grouping)
            else:
                # Dataset No. 1 & 2
                date_list = [ timescale_lower.strftime("%Y-%m-%d"), timescale_upper.strftime("%Y-%m-%d") ]
                n_queries = 1
                self.xvalues_as_datetime = True
                if self.time_wise_grouping == 'date':
                    # Dataset No. 1
                    group_files = True
                    group_by = 'date'
        elif self.time_wise_grouping == "month" or self.time_wise_grouping == "year":
            # Dataset No. 4
            cursor.execute("""SELECT date FROM download ORDER BY date LIMIT 1""")
            timescale_lower_str, = cursor.fetchone()
            timescale_lower = datetime.datetime.strptime(timescale_lower_str, "%Y-%m-%d")
            cursor.execute("""SELECT date FROM download ORDER BY date DESC LIMIT 1""")
            timescale_upper_str, = cursor.fetchone()
            timescale_upper = datetime.datetime.strptime(timescale_upper_str, "%Y-%m-%d")
            date_list = self.__getDateList(timescale_lower, timescale_upper, self.time_wise_grouping, raw_dates=True)
            n_queries = len(date_list) - 1
            group_files = True
            xvalues = self.__getXRange(date_list, self.time_wise_grouping)
        else:
            # Dataset No. 1 & 2
            date_list = None
            n_queries = 1
            self.xvalues_as_datetime = True
            if self.time_wise_grouping == 'date':
                # Dataset No. 1
                group_files = True
                group_by = 'date'
        
        if self.category == "all":
            category = False
        else:
            category = True
            category_list = [self.category] * n_queries
        
        if self.category_wise_grouping:
            if self.time_wise_grouping == 'month' or self.time_wise_grouping == 'year':
                # Dataset No. 6
                group_files = True
                group_by = 'category'
                xvalues = self.__getXRange(date_list, self.time_wise_grouping)
                self.yvalues_as_list = True
            elif self.time_wise_grouping == 'date':
                # Dataset No. 5
                n_queries = 6
                group_files = True
                group_by = 'date'
                category = True
                category_list = self.categoryList
            else:
                # Dataset No. 3
                group_files = True
                group_by = 'category'
                xvalues = self.categoryList
        
        if date_list:
            start_date = True
            end_date = True
        else:
            start_date = False
            end_date = False
        
        for i in range(n_queries):
            arguments = []
            
            if start_date and end_date:
                arguments.extend([date_list[i], date_list[i+1]])
            
            if category:
                arguments.append(category_list[i])
            
            queryStr = self.__generateSQLScript(category, start_date, end_date, group_files, group_by=group_by)
            arg_tuple = tuple(arguments)
            print queryStr, ',', arg_tuple
            cursor.execute(queryStr, arg_tuple)
            
            if len(cursor.description) == 3:
                raw_data = [(date, time, filesize) for (date, time, filesize) in cursor.fetchall()]
                xvalues = [datetime.datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M:%S") for (date, time, filesize) in raw_data]
                yvalues = [filesize for (date, time, filesize) in raw_data]
            elif len(cursor.description) == 2:
                raw_data = [(x, y) for (x, y) in cursor.fetchall()]
                if cursor.description[0][0] == 'date':
                    xvalues = [datetime.datetime.strptime(date, "%Y-%m-%d") for (date, filesize) in raw_data]
                    yvalues = [fs for (date, fs) in raw_data]
                elif cursor.description[0][0] == 'category':
                    category_column = [category_name for (category_name, fs) in raw_data]
                    y = [fs for (category_name, fs) in raw_data]
                    if category_column:
                        for j in range(len(self.categoryList)):
                            if category_column[j] == self.categoryList[j]:
                                continue
                            else:
                                y.insert(j, 0)
                                category_column.insert(j, self.categoryList[j])
                    if self.time_wise_grouping == 'no':
                        yvalues = y
                    else:
                        yvalues.append(y)
            else:
                y, = cursor.fetchone()
                yvalues.append(y)
        
        conn.close()
        
        return (xvalues, yvalues)