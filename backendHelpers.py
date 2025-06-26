import os
import re
import csv

pattern = re.compile(r'.*?\bAudio Archive\s+0*(\d+)\b', re.I)

osDrives = ['Macintosh HD', 'Macintosh HD - Data', '.timemachine']

class BackendHelpers:
    @staticmethod
    def getDrives():
        drives = []
        for drive in os.listdir('/Volumes'):
            if drive not in osDrives:
                t = BackendHelpers.stripDriveName(drive)
                if t != 'Unknown Drive':
                    drives.append(drive)
        return drives
    @staticmethod
    def getMasteringFolder(drive_name):
        masteringFolder = os.path.join('/Volumes', drive_name, 'mastering')
        if not os.path.exists(masteringFolder):
            return None
        return masteringFolder

    @staticmethod
    def stripDriveName(drive_name):
        m = pattern.fullmatch(drive_name.strip())
        if m:
            return f'Audio Archive {int(m.group(1))}'
        return "Unknown Drive"

    @staticmethod
    def getFolderContents(masteringFolder, drive_name):
        if not os.path.exists(masteringFolder):
            return []
        subFolders = []
        for folder in os.listdir(masteringFolder):
            if folder.startswith('.'):
                continue
            subFolders.append((folder, BackendHelpers.stripDriveName(drive_name)))
        return subFolders

    @staticmethod
    def saveToCsv(foldersAndDrives):
        downloads_folder = os.path.expanduser('~/Downloads')
        csv_path = os.path.join(downloads_folder, 'mastering_folders.csv')
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Folder Name', 'Drive Name'])
            for folder, drive in foldersAndDrives:
                writer.writerow([folder, BackendHelpers.stripDriveName(drive)])