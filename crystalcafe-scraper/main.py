from utils import Process
from utils import PortionRetriever
import sys



process = Process("https://crystal.cafe/")
process.process_current_list()
print("Complete!")

# portion = PortionRetriever(10, "crystal.cafe")
# portion.generate_portion()
# print("Complete!")