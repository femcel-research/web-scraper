class UrlPuller:
    """Extracts URLs from a text file"""
    
    def __init__(self, filename):
        """URLs are taken from filename and turned into a list, with values separated by line"""
        self.filename = filename
        self.url_list = []
        self.url_index = 0
        with open(self.filename, 'r') as file:
            for line in file:
                line= line.replace("\n", "")
                self.url_list.append(line)

    def next_url(self):
        """Shifts index for when you want to call get_url on the next entry"""
        self.url_index = self.url_index + 1

    def get_url(self):
        """Returns URL at current index"""
        return self.url_list[self.url_index].strip()
    
    def get_size(self):
        """Returns the number of entries in the list created from the file specified on initialization"""
        return len(self.url_list)
    
    def set_new_file_list(self, filename):
        self.filename = filename
        self.url_list = []
        self.url_index = 0
        with open(self.filename, 'r') as file:
            for line in file:
                self.url_list.append(line)