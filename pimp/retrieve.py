import os, glob

def print_filelist( start_path = "", ext = [] ):
    list = [];

    for path,dirs,files in os.walk( start_path ):
        for filename in files:
            if filename.endswith( tuple(ext) ):
                list.append( os.path.join(path,filename) )

    return list
