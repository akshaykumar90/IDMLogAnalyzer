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
    
    progress    = 0;
    valid_items = 0;
    
    try:
        for f in os.listdir(root_dir):
            if os.path.isdir(os.path.join(root_dir, f)):
                sub_dir = os.path.join(root_dir, f)
                glob_path = os.path.join(sub_dir, "*.log")
                globbed_files = glob.glob(glob_path)
                if len(globbed_files) == 0:
                    # print "No log file exists in %s" % sub_dir
                    print '#',
                    progress = progress + 1
                    if progress % 25 == 0:
                        print progress
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
                    extension = extension[1:]

                    # Select the category of the file based upon the extension
                    # Compressed | Documents | Programs | Music | Video | General
                    if extension in ['zip', 'rar', 'arj', 'gz', 'sit', 'sitx', 'sea', 'ace', 'bz2' '7z']:
                        category = 'Compressed'
                    elif extension in ['doc', 'pdf', 'ppt', 'pps']:
                        category = 'Documents'
                    elif extension in ['mp3', 'wav', 'wma', 'mpa', 'ram', 'ra', 'aac', 'aif', 'm4a']:
                        category = 'Music'
                    elif extension in ['exe', 'msi']:
                        category = 'Programs'
                    elif extension in ['avi', 'mpg', 'mpe', 'mpeg', 'asf', 'wmv', 'mov', 'qt', 'rm', 'mp4', 'flv']:
                        category = 'Video'
                    else:
                        category = 'General'
                    
                    filesize = long(m_size.group(1))/1024
                    
                    query = """insert into download (name, extension, category, date, time, filesize) values (?, ?, ?, ?, ?, ?)"""
                    cursor.execute(query, (shortname, extension, category, str(date), str(time), filesize))
                    print '-',
                    valid_items = valid_items + 1;

                    conn.commit()
                else:
                    print '#',
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

        print progress
        query = """insert into changelog (update_date, new_items) values (?, ?)"""
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " | " + str(valid_items)
        cursor.execute(query, (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), valid_items))
        conn.commit()
    finally:
        conn.close()
    
if __name__ == "__main__": main()
