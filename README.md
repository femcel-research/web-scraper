Terminology
========
**Post**- an original post in a thread/a reply to a post in a thread  

**Thread folder**- a folder within a website subfolder that corresponds to a thread on the website; all links
regardless of highighted comment data will correlate to the same thread folder if they link to the same thread. 

**Snapshot**- a collection of an HTML file, metadata JSON file, and content JSON file that was collected at a specific date/time
(with the three files sharing a folder named after the scan date/time)  

## General thread information
**Board name/["board_name"]**- Name of the board the thread was posted on

**Thread title/["thread_title"]**- Title of thread

**Thread number/["thread_id"]**- Thread identifier derived from its source website

**URL/["url"]**- URL of the thread

## Dates 
**Date published/["date_published"]**- the date a page was published

**Update date/["date_updated"]**- the date a page was last updated

**Date scraped/["date_scraped"]**- the date a page was last scraped

**All post dates/["all_post_dates"]**- set containing dates of when a post was added to the thread

## Post IDs 
**All post IDs/["all_post_ids"]**- set containing IDs from all posts on a thread

**# Posts scanned/["num_all_posts_ids"]**- number of all distinct posts saved in an HTML file/content JSON file  

## Tokens
**Word count of thread/["num_all_words"]**- number of words across all posts

General behavior
========
### Scraping
**Scraping** scrapes a specified website and parses the data from that scrape.

Scraping is enacted through the make target:

    make scrape SITE_NAME="crystal.cafe"

or:

    make scrape

*SITE_NAME is crystal.cafe by default, so override if you want to use a different site.*

### Reparsing
**Reparsing** reparses existing data from their saved HTMLs and saves them in the most up-to-date format.

Reparsing is enacted through the make target:

    make reparse SITE_NAME="crystal.cafe" 

or:

    make reparse

*If SITE_NAME is empty all site data subfolders are reparsed.*

### Portioning thread .txt files
**Portioning** looks through a specified data subfolder or through all subfolders and selects a percentage of the data.

Portioning is enacted through the make target:

    make portion THREAD_PERCENTAGE=10 SITE_NAME="crystal.cafe" RANDOMIZE=1

or:

    make portion

*THREAD_PERCENTAGE, SITE_NAME, and RANDOMIZE are optional. 
If SITE_NAME is empty all site data subfolders are portioned. If RANDOMIZE=0 then randomization is disabled.*


How to read the log files
========
Each log file is named after the scan time and date.  

The log first prints the URLs which have been retrieved into the scan list.  

The scraper processes each URL one-by-one:  
If the URL leads to a valid webpage...  
It checks to see if a thread folder already exists for the thread in the URL.  
If a thread folder does not exist, then it makes a new directory/thread folder.  
It then checks to see if a thread_meta file exists for the thread.  
If a thread_meta file does not exist, it proceeds with a scan.  
If a thread_meta file does exist, but its update_date isn't equal to the update_date of the current webpage, then it proceeds with a scan.  
A new folder is made for each scan with the current time and date.  
HTML info, current webpage scan metadata, and current webpage scan thread content are written to new associated files; the thread_meta file is also written to/updated accordingly.  
The URL of the webpage is added to processed.txt in the data folder.  
When finished, "Generated all scans for thread #___" will be printed — along with the number of total posts (the op and all replies) and the number of new posts that were scanned.  
Finally, the next URL is processed.  

Once all URLs have been processed, the number of functional and broken URLs is printed. As well as the number of new scans that were performed (not skipped due to duplicates or a broken URL).  

A message indicating the scan is complete should finally be printed in the terminal.  

## Errors you may come across  
A critical message "URL list is empty" will print if there are no URLs to scan.  
A warning displaying the webpage's error code will print if there is not content available to scan.  