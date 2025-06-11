# Imports
import json
import logging
import os
import textwrap  # Used for indentation

from datetime import datetime

class MasterTextGenerator:
    """Given a master content JSON, a human-readable file is made.
    
    Once provided a path to a thread's master content (JSON) file, the data
    from that file is used to generate a human-readable and annotatable text
    (TXT) file, for use in ATLAS.ti. The file is written out locally.
    """

    def __init__(self, master_content_path: str, site_dir: str):
        """Uses the data from a master content file for a text file.

        Dependent on a master content file for a thread having already
        been generated. 

        Given the path to a thread's master content (JSON) file, the
        data from that file is used to generate a Master Text File
        according to the specification in this project's documentation.

        Use `write_out()` to write the data out to a formatted text
        file in a folder corresponding to the thread ID in the
        passed `site_dir`.
        
        Args:
            master_content_path (str): Path to a thread's master content file.
            site_dir (str): Parameter for a website's directory.

        Raises:
            Exception: A generic exception for unanticipated errors.
        """
        self.logger = logging.getLogger(__name__)

        data: dict
        self.content: dict

        try:
            # Load master content data
            with open(master_content_path, "r") as file:
                data = json.load(file)
            self.content = data
            # Paths
            thread_id = self.content["thread_id"]
            thread_text_path: str = os.path.join(
                f"{thread_id}",f"master_text_{thread_id}.txt")
            self.master_text_path: str = os.path.join(
                site_dir, thread_text_path)
        except Exception as error:
            self.logger.error(f"Error while initializing text: {error}")
            raise Exception(f"Error while initializing text: {error}")

    def write_text(self):
        """Writes out a human-readable text file based off of content data.
        
        Depends on the `master_text_path` set during initialization, as well
        as the `content` (dictionary of master content data pulled from the
        corresponding JSON file) variable set during initialization.

        Raises:
            Exception: A generic exception for unanticipated errors.
        """
        # Open and write to text file
        separator: str = "\n\n<*><*><*><*><*><*><*><*><*>\n"
        try:
            with open(self.master_text_path, "w") as master_text:
                # ~~ Thread ID header ~~
                master_text.write(
                    f"Thread ID: {self.content["thread_id"]}")
                # Separator
                master_text.write(separator)

                # ~~ Original post ~~
                op: dict = self.content["original_post"]
                # ID
                master_text.write(
                    f"\nOP ID: {op["post_id"]}")
                # (Indented) date
                master_text.write(
                    f"\n  {self._get_date(op["date_posted"])}")
                # (Indented) replied-to list
                master_text.write(
                    f"\n  Replied-to thread IDs: {op["replied_to_ids"]}")
                # Content
                master_text.write(f"\n{op["post_content"]}")
                # Separator
                master_text.write(separator)

                # ~~ Replies ~~
                replies: dict[dict] = self.content["replies"]
                reply_key: str
                for reply_key in replies:
                    reply: dict = replies[reply_key]
                    # ID
                    master_text.write(
                        f"\nReply ID: {reply["post_id"]}")
                    # (Indented) date
                    master_text.write(
                        f"\n  {self._get_date(reply["date_posted"])}")
                    
                    replied_to: list[str] = reply["replied_to_ids"]

                    if not replied_to:
                        # (Indented) replied-to subheader (empty)
                        master_text.write(
                            "\n  Replied-to posts: [N/A]")
                    else: 
                        # (Indented) replied-to subheader
                        master_text.write(
                            "\n  Replied-to posts:")
                        # Quotes of posts being replied to
                        id: str
                        for id in replied_to:
                            post: dict
                            try:
                                post = replies[f"reply_{id}"]
                            except:
                                if id == op["post_id"]:  # Also check OP
                                    post = op
                                else:
                                    post = {
                                        "post_id" : id, 
                                        "post_content" : "[EXTERNAL POST]"}
                            # E.g. `101010 : The quick brown fox jumps over...`
                            quote: str = (
                                f"\n{post["post_id"]} : "
                                f"{post["post_content"]}")
                            # All indented
                            master_text.write(
                                f"\n{textwrap.indent(quote, ' ' * 4)}")
                            master_text.write("\n")
                    self.logger.debug("All replied-to posts have been quoted")
                    #Content
                    master_text.write(f"\n{reply["post_content"]}")
                    # Separator
                    master_text.write(separator)
                # End
                master_text.write("\nEND.")

        except Exception as error:
            self.logger.error(f"Error writing text: {error}")
            raise Exception(f"Error writing text: {error}")
        
    def _get_date(self, date: str) -> str:
        """Returns a more human-readable date.
        
        Assumes the date passed is in YYYY-MM-DDTHH:MM:SS format.

        Args:
            date (str): Date string to be reformatted.
        """
        time: datetime = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
        return datetime.strftime(time, "%Y-%b-%d @%I:%M:%S %p")