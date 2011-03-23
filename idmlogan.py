import getopt
import sys

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
