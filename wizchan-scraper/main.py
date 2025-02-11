from utils import Process
from utils import PortionRetriever

process = Process("https://wizchan.org/")
process.process_current_list()
print("Complete!")

# portion = PortionRetriever(10, "wizchan")
# portion.generate_portion()
# print("Complete!")