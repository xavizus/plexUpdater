import pathlib
import glob
path = pathlib.Path().absolute().as_posix() + "/downloads/PlexMediaServer-*"
currentDownloadedFiles = glob.glob(path)
print(currentDownloadedFiles)