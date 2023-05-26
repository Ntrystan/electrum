#! /usr/bin/env python3
# from https://github.com/signalapp/Signal-Android/blob/2029ea378f249a70983c1fc3d55b9a63588bc06c/reproducible-builds/apkdiff/apkdiff.py

import sys
from zipfile import ZipFile

class ApkDiff:
    IGNORE_FILES = ["META-INF/MANIFEST.MF", "META-INF/CERT.RSA", "META-INF/CERT.SF"]

    def compare(self, sourceApk, destinationApk) -> bool:
        sourceZip      = ZipFile(sourceApk, 'r')
        destinationZip = ZipFile(destinationApk, 'r')

        if self.compareManifests(sourceZip, destinationZip) and self.compareEntries(sourceZip, destinationZip):
            print("APKs match!")
            return True
        else:
            print("APKs don't match!")
            return False

    def compareManifests(self, sourceZip, destinationZip):
        sourceEntrySortedList      = sorted(sourceZip.namelist())
        destinationEntrySortedList = sorted(destinationZip.namelist())

        for ignoreFile in self.IGNORE_FILES:
            while ignoreFile in sourceEntrySortedList: sourceEntrySortedList.remove(ignoreFile)
            while ignoreFile in destinationEntrySortedList: destinationEntrySortedList.remove(ignoreFile)

        if len(sourceEntrySortedList) != len(destinationEntrySortedList):
            print("Manifest lengths differ!")

        for (sourceEntryName, destinationEntryName) in zip(sourceEntrySortedList, destinationEntrySortedList):
            if sourceEntryName != destinationEntryName:
                print(
                    f"Sorted manifests don't match, {sourceEntryName} vs {destinationEntryName}"
                )
                return False

        return True

    def compareEntries(self, sourceZip, destinationZip):
        sourceInfoList      = list(filter(lambda sourceInfo: sourceInfo.filename not in self.IGNORE_FILES, sourceZip.infolist()))
        destinationInfoList = list(filter(lambda destinationInfo: destinationInfo.filename not in self.IGNORE_FILES, destinationZip.infolist()))

        if len(sourceInfoList) != len(destinationInfoList):
            print("APK info lists of different length!")
            return False

        for sourceEntryInfo in sourceInfoList:
            for destinationEntryInfo in list(destinationInfoList):
                if sourceEntryInfo.filename == destinationEntryInfo.filename:
                    sourceEntry      = sourceZip.open(sourceEntryInfo, 'r')
                    destinationEntry = destinationZip.open(destinationEntryInfo, 'r')

                    if not self.compareFiles(sourceEntry, destinationEntry):
                        print(
                            f"APK entry {sourceEntryInfo.filename} does not match {destinationEntryInfo.filename}!"
                        )
                        return False

                    destinationInfoList.remove(destinationEntryInfo)
                    break

        return True

    def compareFiles(self, sourceFile, destinationFile):
        sourceChunk      = sourceFile.read(1024)
        destinationChunk = destinationFile.read(1024)

        while sourceChunk != b"" or destinationChunk != b"":
            if sourceChunk != destinationChunk:
                return False

            sourceChunk      = sourceFile.read(1024)
            destinationChunk = destinationFile.read(1024)

        return True

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: apkdiff <pathToFirstApk> <pathToSecondApk>")
        sys.exit(1)

    if match := ApkDiff().compare(sys.argv[1], sys.argv[2]):
        sys.exit(0)
    else:
        sys.exit(1)
