from datetime import datetime
import json
import os


class SnapshotMetaGenerator:
    def __init__(self, content_json_path: str):
        """
        Given a path to a snapshot content JSON, a meta JSON is generated and returned.

        Args:
        content_json_path (str): Path to snapshot content JSON

        """
        # Opens file at designated path, loads it into data variable, and copies contents into a global var
        with open(content_json_path, "r") as file:
            data = json.load(file)
        self.content_json = data
        self.thread_id = self.content_json["thread_id"]

        # Pathing
        file_name = f"meta_{self.thread_id}.json"
        # Based on assumption that content and meta are stored in same directory
        thread_folder_path = os.path.dirname(content_json_path)
        self.meta_file_path = os.path.join(thread_folder_path, file_name)

        # Posts
        self.original_post: dict = self.content_json["original_post"]
        self.replies: dict = self.content_json["replies"]

    def calculate_num_words(self) -> int:
        """
         Calculates total number of words in a thread.

        Returns:
             num_words (int): Word count of all the words within a thread. Calculated by totaling the word counts of the original post and each reply.
        """

        num_words: int = 0

        # Original post
        original_post_content: str = self.original_post["post_content"]
        original_post_words: list[str] = original_post_content.split()
        original_post_word_count: int = len(original_post_words)

        # Adds word count of OP to total word count of thread
        num_words += original_post_word_count

        # For each reply, calculate its word count and add it to the total word count of the thread.
        for reply in self.replies.values():
            reply_content: str = reply["post_content"]
            reply_words: list[str] = reply_content.split()
            reply_word_count: int = len(reply_words)
            num_words += reply_word_count

        return num_words

    def gather_all_post_ids(self) -> set:
        """
        Gathers all post ids into a set.

        Returns:
            all_post_ids (set[str]): Set containing all post ids

        """

        all_post_ids: set[str] = set()

        # Adds OP post id and reply post ids to a set
        all_post_ids.add(self.original_post["post_id"])

        for reply in self.replies.values():
            all_post_ids.add(reply["post_id"])

        return all_post_ids

    def gather_all_post_dates(self) -> set:
        """
        Gathers all post dates into a set.

        Returns:
            all_post_dates(set[str]): Set containing all post dates

        """
        all_post_dates: set[str] = set()

        # Adds OP post date and reply post dates to a set
        all_post_dates.add(self.original_post["date_posted"])
        for reply in self.replies.values():
            all_post_dates.add(reply["date_posted"])
        return all_post_dates

    def content_to_meta(self) -> None:
        """
        Transfers data from thread contents to a metafile.
        """
        # General board/thread info
        board_name: str = self.content_json["board_name"]
        thread_title: str = self.content_json["thread_title"]
        thread_id: str = self.thread_id
        url: str = self.content_json["url"]

        # Data relating to dates/time:
        date_published: str = self.content_json["date_published"]
        date_updated: str = self.content_json["date_updated"]
        current_date = datetime.now()
        date_scraped: str = current_date.strftime("%Y-%m-%dT%H:%M:%S")
        all_post_dates: set = self.gather_all_post_dates()

        # Data relating to post ids
        all_post_ids: set = self.gather_all_post_ids()
        num_all_post_ids: int = len(all_post_ids)

        # Data relating to word count
        num_all_words: int = self.calculate_num_words()

        metadata = {
            "board_name": board_name,
            "thread_title": thread_title,
            "thread_id": thread_id,
            "url": url,
            "date_published": date_published,
            "date_updated": date_updated,
            "date_scraped": date_scraped,
            "all_post_dates": all_post_dates,
            "all_post_ids": all_post_ids,
            "num_all_post_ids": num_all_post_ids,
            "num_all_words": num_all_words,
        }

        self.meta_dump(metadata)

    def meta_dump(self, metadata: dict) -> None:
        """Dumps website metadata into a JSON file.

        Args:
            metadata (dict): Dictionary containing metadata values.
        """
        with open(self.meta_file_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
