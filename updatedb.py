import os
import re
import glob
import datetime
import sqlite3

def main():
    root_dir = "C:\Users\AKSHAY\AppData\Roaming\IDM\DwnlData\AKSHAY"
    db_filename = 'logan.db'
    
    time_pattern = re.compile(r"Time: (.*)$", re.MULTILINE)
    name_pattern = re.compile(r"^Rename temp file (?:.*?) to (.*?)\.$", re.MULTILINE)
    size_pattern = re.compile(r"^Download complete. Downloaded (\d*) Bytes Total$", re.MULTILINE)
    
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    
    progress = 0;
    
    try:
        for f in os.listdir(root_dir):
            if os.path.isdir(os.path.join(root_dir, f)):
                sub_dir = os.path.join(root_dir, f)
                glob_path = os.path.join(sub_dir, "*.log")
                globbed_files = glob.glob(glob_path)
                if len(globbed_files) == 0:
                    print "No log file exists in %s" % sub_dir
                    continue
                log_file_path = globbed_files[0]
                
                log_file = open(log_file_path, "r")
                log_file_str = log_file.read()
                log_file.close()
                
                m_time = time_pattern.search(log_file_str)
                m_name = name_pattern.search(log_file_str)
                m_size = size_pattern.search(log_file_str)
                
                if m_time and m_name and m_size:
                    date_str_list = m_time.group(1).split()
                    date_str_list[3] = date_str_list[3][:date_str_list[3].find('.')]
                    date_str = " ".join(date_str_list[:5])
                    fmtstring = "%a %b %d %H:%M:%S %Y"
                    downloaded_on = datetime.datetime.strptime(date_str, fmtstring)
                    date = downloaded_on.date()
                    time = downloaded_on.time()
                    
                    name = m_name.group(1)
                    (filepath, filename) = os.path.split(name)
                    (shortname, extension) = os.path.splitext(filename)
                    
                    filesize = long(m_size.group(1))/1024
                    
                    query = """insert into download (name, filetype, date, time, filesize) values (?, ?, ?, ?, ?)"""
                    cursor.execute(query, (filename, extension, str(date), str(time), filesize))
                    # print filename + " | " + extension + " | " + str(downloaded_on) + " | " + str(filesize)
                    print '-',

                    conn.commit()
                else:
                    print '*',
                    # print "Malformed Log File %s" % log_file_path
                    # if not m_time:
                        # print "m_time not found"
                    # if not m_name:
                        # print "m_name not found"
                    # if not m_size:
                        # print "m_size not found"

                progress = progress + 1
                if progress % 25 == 0:
                    print progress
    finally:
        conn.close()
    
if __name__ == "__main__": main()
