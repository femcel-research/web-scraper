from datetime import datetime

import json
import logging
import os

logger = logging.getLogger(__name__)

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
        try:
            self.thread_id = self.content_json["thread_id"]
            logger.debug(f"Thread ID located: {self.thread_id}")
        except Exception as error:
            logger.error(f"Error finding 'thread_id' in {content_json_path}: {error}")
            raise KeyError(f"Error finding 'thread_id' in {content_json_path}: {error}")

        # Pathing: Based on assumption that content and meta are stored in same directory
        file_name = f"meta_{self.thread_id}.json"
        thread_folder_path = os.path.dirname(content_json_path)
        self.meta_file_path = os.path.join(thread_folder_path, file_name)
        logger.debug(f"File path for meta is denoted as: {self.meta_file_path}")

        # Posts
        try:
            self.original_post: dict = self.content_json["original_post"]
            logger.info(f"Original post located.")
        except Exception as error:
            logger.error(f"Error finding 'original_post' in {content_json_path}: {error}")
            raise KeyError(f"Error finding 'original_post' in {content_json_path}: {error}")
        
        try:
            self.replies: dict = self.content_json["replies"]
            logger.info(f"Replies located.")
        except Exception as error:
            logger.error(f"Error finding 'replies' in {content_json_path}: {error}")
            raise KeyError(f"Error finding 'replies' in {content_json_path}: {error}")

    # Helper functions:
    def calculate_num_words(self) -> int:
        """Calculates total number of words in a thread. 
        
        Calculated by totaling the word counts of the original post 
        and each reply.
        
        Returns:
            num_words (int): Word count of all the words within a thread.
        """

        num_words: int = 0

        # Original post
        try: 
            original_post_content: str = self.original_post["post_content"]
            original_post_words: list[str] = original_post_content.split()
            original_post_word_count: int = len(original_post_words)
            logger.debug(f"Word count for original post calculated: {original_post_word_count} word(s)")

            # Adds word count of OP to total word count of thread
            num_words += original_post_word_count

        except Exception as error:
            logger.error(f"Error finding 'post_content' in original post: {error}")
            raise KeyError(f"Error finding 'post_content' in original post: {error}")

        
        # For each reply, calculate its word count and add it to the total word count of the thread.
        for reply in self.replies.values():
            try: 
                reply_content: str = reply["post_content"]
                reply_words: list[str] = reply_content.split()
                reply_word_count: int = len(reply_words)
                logger.debug(f"Word count for reply calculated: {reply_word_count} word(s)")
                
                # Adds word count of reply to total word count of thread
                num_words += reply_word_count
            
            except Exception as error:
                logger.error(f"Error finding 'post_content' in reply: {error}")
                raise KeyError(f"Error finding 'post_content' in reply: {error}")

        return num_words

    def gather_all_post_ids(self) -> set:
        """
        Gathers all post ids into a set.

        Returns:
            all_post_ids (set[str]): Set containing all post ids

        """

        all_post_ids: set[str] = set()

        # Adds OP post id and reply post ids to a set
        try:
            original_post_id: str = self.original_post["post_id"]
            all_post_ids.add(original_post_id)
            logger.debug(f"Original post ID {original_post_id} added to all_post_ids set.")
        except Exception as error:
            logger.error(f"Error finding 'post_id' in original post: {error}")
            raise KeyError(f"Error finding 'post_id' in original post: {error}")

        for reply in self.replies.values():
            try:
                reply_id: str = reply["post_id"]
                all_post_ids.add(reply_id)
                logger.debug(f"Reply ID {reply_id} added to all_post_ids set.")
            except Exception as error:
                logger.error(f"Error finding 'post_id' in reply: {error}")
                raise KeyError(f"Error finding 'post_id' in reply: {error}")

        return all_post_ids

    def gather_all_post_dates(self) -> set:
        """
        Gathers all post dates into a set.

        Returns:
            all_post_dates(set[str]): Set containing all post dates

        """
        all_post_dates: set[str] = set()

        # Adds OP post date to all_post_dates set
        try:
            original_post_date_posted = self.original_post["date_posted"]
            all_post_dates.add(original_post_date_posted)
            logger.debug(f"OP post date {original_post_date_posted} added to all_post_dates set.")
        except Exception as error:
            logger.error(f"Error finding 'date_posted' in original post: {error}")
            raise KeyError(f"Error finding 'date_posted' in original post: {error}")

        # Adds post date of all replies to all_post_dates set
        for reply in self.replies.values():
            try:
                reply_date_posted = reply["date_posted"]
                all_post_dates.add(reply_date_posted)
            except Exception as error:
                logger.error(f"Error finding 'date_posted' in reply: {error}")
                raise KeyError(f"Error finding 'date_posted' in reply: {error}")
        return all_post_dates

    def meta_dump(self) -> None:
        """Dumps thread metadata into a JSON file.
        """
        meta: dict = self._generate_meta()
        with open(self.meta_file_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
    
    def get_path(self) -> str:
        return self.meta_file_path

    # Main method:
    def _generate_meta(self) -> dict:
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
        date_scraped: str = self.content_json["date_scraped"]
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
            "all_post_dates": list(all_post_dates),
            "all_post_ids": list(all_post_ids),
            "num_all_post_ids": num_all_post_ids,
            "num_all_words": num_all_words,
        }

        return metadata

    
