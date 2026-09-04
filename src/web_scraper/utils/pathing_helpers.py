import os
import glob
from datetime import *
from pathlib import Path

# Directories 
def directoryExists (dir: str) -> bool:
    """
    Checks if a given directory path exists.
    
    Args:
        dir: directory path
    
    Returns:
        bool: Indicates whether the path exists
    """

    return os.path.exists(dir)

def subdirectorySearch(dir: str) -> list:
    """
    Searches for any subdirectories within a given directory.
    
    Args:
        dir: directory path
    
    Returns:
        list: List of found directories
    """
    return [directory for directory in Path(dir).iterdir() if directory.is_dir()]

def makeDirectory(dir: str):
    """
    Makes a directory using a given path.
    
    Args:
        dir: directory path
    """
    os.makedirs(dir, exist_ok=True)

def getRecentSubdirectory (listOfSubdirs: list) -> str:
    """
    Retrieves the most recently modified subdirectory given a list of subdirectories.
    
    Args:
        listOfSubdirs: list of subdirectory paths
    
    Returns:
        str: path of most recently edited subdirectory
    """
    return max(listOfSubdirs, key=os.path.getmtime)

# Modification Time
def getModificationTime (dir: str) -> float:
    """
    Retrieves the modification time of a given directory
    
    Args:
        dir: directory path
    
    Returns:
        float: last modification time as a floating-point value
    """
    return os.path.getmtime(dir)

def modificationTimeToDatetime (modTime: float):
    """
    Converts floating point modification time to a datetime object
    
    Args:
        modTime: modification time
    
    Returns:
        datetime: modification time as a datetime object
    """
    return datetime.fromtimestamp(modTime)

# Thread Pathing
def getThreadPath (siteName: str, threadId: str) -> str:
    """
    Configures a thread directory path given a site name str and thread id str.

    Args:
        siteName: str containing site name
        threadId: str containing thread id

    Returns:
        str: file path to a thread directory
    """

    return os.path.join(f"./data/{siteName}", threadId)

def getThreadSnapshotPath(threadPath: str, scanTimeStr: str) -> str:
    """
    Configures a thread snapshot path given a thread directory path and scan time string.

    Args:
        threadPath: string contianing path to a thread directory
        scanTimeStr: str containing time of last scan

    Returns:
        str: file path to a thread snapshot at a given time

    """
    return os.path.join(threadPath, scanTimeStr)

def getContentFilePath (threadSnapshotPath: str, threadId: str) -> str:
    """
    Configures a thread content file path given a thread snapshot path and thread id string.

    Args:
        threadSnapshotPath: string contianing path to a thread snapshot directory
        threadId: str containing thread id

    Returns:
        str: file path to a thread content file

    """
    return os.path.join(
        threadSnapshotPath, f"content_{threadId}.json"
    )

def getCandidateContentFiles (thread_dir: str) -> list[str]:
    """
    Retrieves eligible files containing the phrase 'content_*.json'
    Args:
        thread_dir: thread folder to search in
    Returns:
        list[str]: list containing snapshot content file paths
    """
    search_str = os.path.join(thread_dir, "**", "content_*.json")
    return list(glob.glob(search_str, recursive=True))

def getMasterVersionPath (thread_dir: str, thread_id: str) -> str:
    """
    Configures a thread master version file path given a thread id string.
    
    Args:
        thread_dir: thread folder to search in
        threadId: str containing thread id
    
    Returns:
        str: file path to a thread content file
    
    """
    return os.path.join(thread_dir, f"master_version_{thread_id}.json")

def getCandidateMetaFiles (thread_dir: str) -> list[str]:
    """
    Retrieves eligible files containing the phrase 'meta_*.json'
    Args:
        thread_dir: thread folder to search in
    Returns:
        list[str]: list containing meta file paths
    """
    search_str = os.path.join(thread_dir, "**", "meta_*.json")
    return list(glob.glob(search_str, recursive=True))
