web-scraper
========
## Overview
Using web-scraper, you can **scrape and parse** threads from chan-style 
websites, and **reparse** HTML files previously scraped from chan-style 
websites. You can also **portion** out TXT files from previously parsed 
thread data for annotating purposes. 
  
In order to do either, within the `data/` directory (submodule), you must 
ensure you have a `data/params/` subdirectory that is populated with a 
parameter file corresponding to each website you would like to scrape/parse 
thread data from. You can create new parameter files for each chan-style 
website you would like to scrape/parse thread data from, or you can use the 
parameter files in the Google Drive folder for this project (`./params/`).  

## How to Use
Scraping/parsing, reparsing, and portioning will be performed using Makefile 
commands. It is recommended that you run any commands in a Python virtual 
environment.

### Setup
```
make setup
```
Installs the project and all of its dependencies.

### Reparsing
```
make reparse
``` 
Looks at every parameter file in `data/params/` and navigates to a 
subdirectory corresponding to each parameter file (if possible). Thread 
data is then parsed from every HTML file (in every snapshot folder), and all 
new files are generated with each referenced HTML snapshot.

It is recommended that you run `make reparse` on any prior data before 
scraping/parsing new data, or you run `make all` (below).

### Scrape/Parse
```
make scrape
``` 
(NO ARGS) Looks at every parameter file in `data/params/` and fetches the 
homepage specified in each file. Thread URLs are then retrieved and navigated 
to, whereupon each thread URLs HTML data is downloaded and thread data is 
parsed into a snapshot subdirectory (itself within a thread subdirectory) 
titled with the date and time the command was run.  

OR

```
make scrape SITE_NAME=<param_prefix>
``` 
(WITH ARGS) Does the same as `make scrape` (NO ARGS), but for a single 
parameter file.
  
A tree illustrating the result of `make scrape SITE_NAME=example` can be 
seen below:

```
data/
├─ params/
│  ├─ example_params
├─ example/
│  ├─ (THREAD_ID)/
│  │  ├─ (DATE_TIME)/
│  │  │  ├─ HTML
│  │  │  ├─ content
│  │  │  ├─ metadata
│  │  ├─ (DATE_TIME)/
│  │  ├─ master_content
│  │  ├─ master_metadata
│  │  ├─ master_text
│  │  ...
```  
  
For more information on what each output file contains, please reference 
the project's documentation.

### Calculate Sitewide Statistics
```
make calculate_sitewide
``` 
(NO ARGS) Looks at every parameter file in `data/params/` and uses all of the 
master metadata files in each site's subdirectory to calculate general 
statistics relating to the collected data.

OR

```
make calculate_sitewide SITE_NAME=<param_prefix>
``` 
(WITH ARGS) Does the same but for a single parameter file.

### Setup, Reparse, Scrape/Parse, Calculate Sitewide Statistics
```
make all
``` 
Runs `make setup`, `make reparse`, `make scrape` (NO ARGS), 
and `make calculate_sitewide` (NO ARGS).

**It is recommended that you run `make all` once to get everything 
set up if you are transitioning to using this version of web-scraper 
from a previous version (and you have a backlog of data).** 

### Scrape/Parse, Calculate Sitewide Statistics
```
make scrape_calculate
``` 
Runs `make scrape` (NO ARGS) and `make calculate_sitewide` (NO ARGS).

**If you are looking to scrape/parse from the chan-style sites with parameter 
files in `data/params/` at regular intervals, it is recommended that you 
use this command.**

### Portion
```
make portion
``` 
(NO ARGS) Duplicates the master text file from 10% of each site's thread 
subdirectories into a new subdirectory, `data/portions/`. 

The IDs of threads which have already been duplicated are logged so threads 
aren't portioned out more than once.

OR

```
make portion THREAD_PERCENTAGE=<percentage> PORTION_DIRECTORY=<dir> SITE_NAME=<param_prefix>
```
(WITH ARGS) Does the same as `make portion` (NO ARGS), but the percentage 
of data you wish to duplicate is specified, the data is duplicated into the 
directory specified, and the specific site you with to have data portioned 
from is specified.

Terminology
========
**Post**: an original post in a thread/a reply to a post in a thread  

**Thread folder**: a folder within a website subfolder that corresponds 
to a thread on the website; all links
regardless of highighted comment data will correlate to the same thread 
folder if they link to the same thread. 

**Snapshot**: a collection of an HTML file, metadata JSON file, and content 
JSON file that was collected at a specific date/time
(with the three files sharing a folder named after the scan date/time)  

## General thread information
**Board name/["board_name"]**: Name of the board the thread was posted on

**Thread title/["thread_title"]**: Title of thread

**Thread number/["thread_id"]**: Thread identifier derived from its source website

**URL/["url"]**: URL of the thread

## Dates 
**Date published/["date_published"]**: The date a page was published

**Update date/["date_updated"]**: The date a page was last updated

**Date scraped/["date_scraped"]**: The date a page was last scraped

**All post dates/["all_post_dates"]**: Set containing dates of when a post was added to the thread

## Post IDs 
**All post IDs/["all_post_ids"]**: Set containing IDs from all posts on a thread

**# Posts scanned/["num_all_posts_ids"]**: Number of all distinct posts saved in an HTML file/content JSON file  

## Words
**Word count of thread/["num_all_words"]**: Number of words across all posts

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