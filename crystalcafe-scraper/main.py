from utils.processing.Process import Process
from utils import PortionRetriever
import sys

process = Process("https://crystal.cafe/")
process.process_existing_files()
process.process_current_list()
print("Complete!")
