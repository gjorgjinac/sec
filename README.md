
STRUCTURE:

The final results can be found in the extracted_data.txt file

'litigations' is a django app that enables the database connection (https://www.djangoproject.com/)

'mining' is a scrapy app that crawls 'sec.gov' (https://scrapy.org/)
  The parsing is done with the LitigationsDetailSpider (sec\mining\mining\spiders\litigations_detail_spider). 
	
  The parse_master function collects data (release_no, date and respondents) from 
  'https://www.sec.gov/litigation/litreleases/litrelarchive/litarchiveXXXX.shtml' (where XXXX is the year, 1995<=XXXX<=2018)
  and sends requests for additional data (titles, content, references) for each litigation, which are later processed by the 
  parse_detail function. 
	
  The items are then sent to the pipeline to be written in the database (sec\mining\mining\pipelines.py)
  The spider also uses processing functions defined for each item class in sec\mining\mining\items.py
 
 
HOW TO USE:

To start the crawler, you need to run 'scrappy crawl detail' from the sec/mining directory 

To save the scrapped information to the database you need to remove the "not" keyword from
if not spider.name == "detail":
in the sec/mining/mining/pipelines.py file

The download delay is currently set to 0. 
To add delays between requests, set the maximum number of concurrent requests, or enable autothrottle,
you need to change the sec/mining/mining/settings.py file

Further instructions that are not specific to this project can be found in the documentation of 
scrapy(https://scrapy.org/) and django(https://www.djangoproject.com/):

https://goo.gl/Xy66GS
