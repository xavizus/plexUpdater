# This is the first!
# Api to get urls: https://plex.tv/api/downloads/5.json?channel=plexpass&_=1586692695835

import requests
import json
import platform
import os as OS
import subprocess
import glob
import pathlib
from urllib.parse import urlparse

# get data from request url
def getRequestData(url, payload):
    print("Getting request data...")
    data = requests.get(url, params=payload)
    return data.json()

# get url and filename
def getUrlAndFileName(data, os, build = None, distro = None):
    print("Getting URL and filename...")
    allowedOS = ['Windows', 'MacOS', 'Linux', 'Darwin']
    if os not in allowedOS:
        oses = ", ".join(allowedOS)
        raise Exception('You supplied the os {}, which is not in the list. Allowed OS:s are: {}'.format(os, oses))
    if(os == 'Darwin'):
        os = 'MacOS'
    
    releases = data['computer'][os]['releases']
    url = ''
    if os != 'Linux':
        url = releases[0]['url']
    else:
        for release in releases:
            if release['build'] == build and release['distro'] == distro:
                url = release['url']
                break
    filename = url[url.rfind("/")+1:]

    if url == '':
        raise Exception('Did not get download URL!')
    return url, filename

# Download the file
def downloadFile(url,filename):
    print("Downloading file..")
    path = pathlib.Path().absolute().as_posix() + "/downloads/plexmediaserver-*"
    currentDownloadedFiles = [OS.path.basename(x) for x in glob.glob(path)]
    if filename in currentDownloadedFiles:
        raise Exception('No new files found!')
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception('Could not get download. Got HTTP code: {}'.format(response.status_code))
    print(response.headers['content-type'])
    if not OS.path.exists('downloads'):
        OS.mkdir('downloads')
    with open('downloads/'+filename, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=52428800):
            fd.write(chunk)

# Run commands
def runCommands(commands: list) ->int:
    process = subprocess.Popen(commands, stdout=subprocess.PIPE,universal_newlines=True)
    while True:
        output = process.stdout.readline()
        print(output.strip())
        return_code = process.poll()
        if return_code is not None:
            print('Return code: ', return_code)
            for output in process.stdout.readlines():
                print(output.strip())
            return return_code

# install or update plex
def installOrUpdatePlex(filename):
    print("Installing...")
    downloadFolder = pathlib.Path().absolute().as_posix() + "/downloads/" + filename
    install = runCommands(['sudo', 'yum', 'localinstall', downloadFolder, '-y'])
    if install != 0:
        raise Exception('Could not install PlexMediaServer!')
    
    print("Starting program...")
    runCommands(['sudo', 'systemctl', 'start', 'plexmediaserver'])
    runCommands(['sudo', 'systemctl', 'enable', 'plexmediaserver'])
try:    
    payload = {'channel': 'plexpass', '_': '1586692695835'}
    url = 'https://plex.tv/api/downloads/5.json'
    dictData = getRequestData(url, payload)
    url, filename = getUrlAndFileName(dictData, platform.system(), 'linux-x86_64', 'redhat')
    print("URL: {} \nFilename: {}".format(url, filename))
    downloadFile(url,filename)
    installOrUpdatePlex(filename)
except Exception as identifier:
    print(identifier)