from ftplib import FTP

def print_filelist( host, username, password ):
    ftp = FTP(host)                 # connect to host, default port
    ftp.login(username, password)   # user anonymous, passwd anonymous@
    return
