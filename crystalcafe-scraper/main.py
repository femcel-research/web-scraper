from utils.parsing.Parse import Parse
from utils import PortionRetriever
import sys

parse = Parse("https://crystal.cafe/")
parse.process_existing_files()
parse.process_current_list()
print("Complete!")
