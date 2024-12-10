# web-scraper
## How to read the log files/general behavior  
### Typical output  
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

### Scan terminology  
**scan** a collection of an html file, metadata file, and content file that was collected at a specific date/time
(with the three files sharing a folder named after the scan date/time)  
**post** an original post in a thread/a reply to a post in a thread  
**# posts scanned** number of posts saved in an html file/content file  
**thread folder** a folder within a website subfolder that corresponds to a thread on the website; all links
regardless of highighted comment data will correlate to the same thread folder if they link to the same thread.  
**update date/["update_date"]** the date a page was last updated, according to its html file  

### Errors you may come across  
A critical message "URL list is empty" will print if there are no URLs to scan.  
A warning displaying the webpage's error code will print if there is not content available to scan.  

## How to read different meta values  
### thread_meta file  
**["dist_post_ids"]** is the list of distinctive post_ids accross all scans for a single thread  
**["lost_post_ids"]** (untested) is a list of post_ids that are in ["dist_post_ids"], but not a subsequent scan (also needs to not alread be in ["lost_post_ids"] already)  
**["num_dist_posts"]** is a count that gets added to using ["num_new_posts"] on every scan  
**["num_total_posts"]** is a count that gets added to using ["num_all_posts"] on every scan  
**["num_lost_posts"]** is a count of every post that was formerly scanned for the current thread, but was not in a subsequent scan  
### scan_meta file  
**["all_post_ids"]** is a list of all post_ids (including post_ids that were in prior scans) that were scanned  
**["new_post_ids"]** is a list of post_ids that were scanned and didn't already exist in ["dist_post_ids"]  
**["new_lost_posts"]** (untested) is a list of post_ids that are in ["dist_post_ids"], but not this scan (also needs to not alread be in ["lost_post_ids"] already)  
**["num_all_posts"]** is a count of all posts that were scanned  
**["num_new_posts"]** is a count of all posts that were scanned and didn't already exist in ["dist_post_ids"]  
**["num_new_lost_posts"]** is a count of all posts that are in ["dist_post_ids"], but not this scan (also needs to not alread be in ["lost_post_ids"] already)  
### site_meta file  
(WIP) **["num_sitewide_threads"]** is a count of all threads (Can't confirm implementation due to 504)  
**["num_sitewide_total_posts"]** is a count of all posts across all scans (including duplicates) across all threads  
(WIP) **["num_sitewide_dist_posts"]** is a count of all posts across all scans across all threads (only counting 1 per set of duplicates) (Can't confirm implementation due to 504)  

## Other data collected  
In addition to the statistics above, a complete scan of each webpage's HTML is collected with each processing. Additional metadata regarding thread number, etc. is also saved alongside the above statistics in the associated meta JSON files with each scan — as well as a parsed JSON file containing the posts in the scanned thread.  

Each thread can be scanned multiple times, depending on when previous scans were/if a scan was already performed at a specified update_date. As scans are performed using homepage URLs in descending order, each scan of a particular thread will be performed using the most up-to-date version of the thread.

## JSON Parameters for different imageboard homepages (WIP)
Note that not all homepages have a keywords and/or description attribute in their meta information.  
At this point the scraper only works with homepages, but we always have the option of adding other parameters to
make it easier to toss in catalogs.  
**["file_name"]** name of the folder website data will be found in, as well as the prefix for the sitewide meta file  
**["url"]** website url  
**["domain"]** used to append to relative urls  
**["container"]** name of class for location of links on the homepage ("box right")  
**["op"]** name of class for original posts ("post op")  
**["op_id_prefix"]** prefix for ids of original posts (""(crystal, lolcow) and "op_"(wizchan))  
**["reply"]** name of class for post replies ("post reply")  
**["reply_id_prefix"]** prefix for ids of post replies ("reply_")  
**["post_date_location"]** class/label "time datetime= " is in ("label for= delete_**op_id**" and "class_="post_no date-link"")  
**["highlighted_post"]** name of class for highlighted post ("post reply  highlighted"[sic] and "post reply highlighted") **May be not be needed if the highlight is parsed from the url**