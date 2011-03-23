import matplotlib.dates as mpldates
import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter, DayLocator, HourLocator
from matplotlib.dates import MONDAY

class LineChart:
    def __init__(self, xvalues, yvalues, timescale, use_plot_date):
        self.xvalues = xvalues
        self.yvalues = yvalues
        self.timescale = timescale
        self.use_plot_date = use_plot_date
    
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
            ax.set_xticklabels(self.xvalues)
        
        ax.autoscale_view()
        ax.grid(True)
        fig.autofmt_xdate()

        plt.show()