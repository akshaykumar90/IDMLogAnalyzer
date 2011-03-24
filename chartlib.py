import matplotlib.dates as mpldates
import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter, DayLocator, HourLocator
from matplotlib.dates import MONDAY
from matplotlib.ticker import MultipleLocator, FuncFormatter

class LineChart:
    def __init__(self, xvalues, yvalues, use_plot_date, **kwargs):
        self.xvalues = xvalues
        self.yvalues = yvalues
        self.use_plot_date = use_plot_date
        if use_plot_date:
            self.timescale = kwargs['timescale']
    
    def __scale_yvalues(self, ymax):
        ONE_GB              = 1048576
        SCALE_ALLOWED       = [1, 2, 4, 8, 10]
        MAX_TICKS_ALLOWED   = 15
        
        # GB ticks required for ymax
        ticks_req = int( ymax / ONE_GB ) + 1
        
        for i in SCALE_ALLOWED:
            if ticks_req / i > MAX_TICKS_ALLOWED:
                continue
            else:
                break
        
        return i
    
    def draw(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        if self.use_plot_date:
            self.xvalues = mpldates.date2num(self.xvalues)
            ax.plot_date(self.xvalues, self.yvalues, '-')
            
            months  = MonthLocator()
            mondays = WeekdayLocator(MONDAY)
            days    = DayLocator()
            hours   = HourLocator(interval=6)
            
            monthsFmt   = DateFormatter("%b '%y")
            daysFmt     = DateFormatter("%m/%d")
            
            if self.timescale == 'all' or self.timescale == 'year':
                ax.xaxis.set_major_locator(months)
                ax.xaxis.set_major_formatter(monthsFmt)
                ax.xaxis.set_minor_locator(mondays)
            elif self.timescale == 'month':
                ax.xaxis.set_major_formatter(daysFmt)
                ax.xaxis.set_major_locator(mondays)
                ax.xaxis.set_minor_locator(days)
            else:
                ax.xaxis.set_major_locator(days)
                ax.xaxis.set_major_formatter(daysFmt)
                ax.xaxis.set_minor_locator(hours)
        else:
            ax.plot(self.yvalues)
            ax.set_xticks(range(len(self.xvalues)))
            ax.set_xticklabels(self.xvalues)
            
        def format_func(x, pos):
            return x / 1048576 # = 1024 * 1024 KB = 1 GB
        
        l, u = ax.get_ylim()
        GB_scale_req = self.__scale_yvalues(u)
        GB_Locator = MultipleLocator(1048576 * GB_scale_req)
        
        ax.yaxis.set_major_locator(GB_Locator)
        formatter = FuncFormatter(format_func)
        ax.yaxis.set_major_formatter(formatter)
        
        ax.autoscale_view()
        ax.grid(True)
        fig.autofmt_xdate()

        plt.show()

class BarChart:
    def __init__(self, xvalues, yvalues, stacked_bar_graph=False):
        self.xvalues = xvalues
        self.yvalues = yvalues
        self.stacked_bar_graph = stacked_bar_graph
    
    def __scale_yvalues(self, ymax):
        ONE_GB              = 1048576
        SCALE_ALLOWED       = [1, 2, 4, 8, 10]
        MAX_TICKS_ALLOWED   = 15
        
        # GB ticks required for ymax
        ticks_req = int( ymax / ONE_GB ) + 1
        
        for i in SCALE_ALLOWED:
            if ticks_req / i > MAX_TICKS_ALLOWED:
                continue
            else:
                break
        
        return i
    
    def draw(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        width = 0.8
        locs = range(1, len(self.xvalues) + 1)
        if self.stacked_bar_graph == False:
            ax.bar(locs, self.yvalues, width=width)
        else:
            colors = ['b','g','c','m','r','y']
            for i in range(len(self.xvalues)):
                bottom = 0
                k = 0
                patches = []
                for j in self.yvalues[i]:
                    p = ax.bar(i+1, j, bottom=bottom, width=width, color = colors[k])
                    patches.append(p)
                    bottom = bottom + j
                    k = k + 1
            leg = plt.legend(tuple(patches), ('Compressed', 'Documents', 'General', 'Music', 'Programs', 'Video'), loc='best')
            leg.get_frame().set_alpha(0.4)
        ticks_loc = [i + width / 2 for i in locs]
        ax.set_xticks(ticks_loc)
        ax.set_xticklabels(self.xvalues)
        
        def format_func(x, pos):
            return x / 1048576 # = 1024 * 1024 KB = 1 GB
        
        l, u = ax.get_ylim()
        GB_scale_req = self.__scale_yvalues(u)
        GB_Locator = MultipleLocator(1048576 * GB_scale_req)
        
        ax.yaxis.set_major_locator(GB_Locator)
        formatter = FuncFormatter(format_func)
        ax.yaxis.set_major_formatter(formatter)
        
        ax.autoscale_view()
        ax.grid(True)
        fig.autofmt_xdate()
        
        plt.show()
