import getopt
import sys
from SqliteInterface import SqliteInterface
import chartlib

def main(argv):
    LINE_PLOT = 0
    BAR_PLOT  = 1
    PIE_PLOT  = 2
    
    timescale = 'all'
    time_wise_grouping = 'date'
    category_wise_grouping = False
    category = 'all'
    sqli_kwargs = {}
    db_filename = 'logan.db'
    
    try:
        opts, args = getopt.getopt(argv, "hlbpay:m:w:g:c:d:", \
        ["help", "line", "bar", "pie", "all", "year=", "month=", "week=", "group=", "category=", "database="])
    except getopt.GetoptError:
        sys.exit(2)
    
    for opt,arg in opts:
        if opt in ("-l", "--line"):
            # Line Chart
            chart_type = LINE_PLOT
        elif opt in ("-b", "--bar"):
            # Bar Chart
            chart_type = BAR_PLOT
        elif opt in ("-p", "--pie"):
            # Pie Chart
            chart_type = PIE_PLOT
        elif opt in ("-a", "--all"):
            # Plot All Time data
            timescale = "all"
        elif opt in ("-m", "--month"):
            # Plot only for `arg` month
            timescale = "month"
            sqli_kwargs['period'] = arg
        elif opt in ("-y", "--year"):
            # Plot only for `arg` year
            timescale = "year"
            sqli_kwargs['period'] = arg
        elif opt in ("-w", "--week"):
            # Plot only for `arg` week
            timescale = "week"
            sqli_kwargs['period'] = arg
        elif opt in ("-g", "--group"):
            group_by = arg.split(',')
            if 'category' in group_by:
                category_wise_grouping = True
                group_by.remove('category')
            time_wise_grouping = group_by.pop()
        elif opt in ("-c", "--category"):
            category = arg
        elif opt in ("-d", "--database"):
            db_filename = arg
    
    data_model = SqliteInterface(db_filename, timescale, category, time_wise_grouping, \
                                 category_wise_grouping, **sqli_kwargs)
    xvalues, yvalues = data_model.getData()
    
    if chart_type == LINE_PLOT:
        lc_kwargs = {}
        use_plot_date = data_model.get_xvalues_type()
        if use_plot_date:
            lc_kwargs['timescale'] = timescale
        lc = chartlib.LineChart(xvalues, yvalues, use_plot_date, **lc_kwargs)
        lc.draw()
    elif chart_type == BAR_PLOT:
        stacked_bar_graph = data_model.get_yvalues_type()
        bc = chartlib.BarChart(xvalues, yvalues, stacked_bar_graph)
        bc.draw()
    elif chart_type == PIE_PLOT:
        pc = chartlib.PieChart(xvalues, yvalues)
        pc.draw()

if __name__=="__main__": main(sys.argv[1:])
