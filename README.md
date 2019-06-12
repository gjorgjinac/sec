# Sec Litigation Crawler
### A project for the course Web Programming at FCSE, Skopje
#### Students invovled, ordered by their index numbers:
  - 161517, Ѓорѓина Цениќ
  - 161528, Филип Маркоски


### Structure
'litigations' is a django app that enables the database connection (https://www.djangoproject.com/)
'mining' is a scrapy app that crawls 'sec.gov' (https://scrapy.org/)
The parsing is done with the LitigationsDetailSpider (mining\mining\spiders\litigations_detail_spider).
The parse_master function collects data (release_no, date and respondents) from
'https://www.sec.gov/litigation/litreleases/litrelarchive/litarchiveXXXX.shtml' (where XXXX is the year, 1995<=XXXX<=2018)
and sends requests to get additional data (titles, content, references) for each litigation, which are later processed by the
parse_detail function. The parsing functions handle the inconsistencies in the website listed in the issues_checklist.txt file.
The pieces of data are stored in item loaders which apply a series of processing functions defined
for each item class in sec\mining\mining\items.py.
The items are written to the database using the process_item function in the MiningPipeline (sec\mining\mining\pipelines.py)

### How to use
##### Configure the database in `sec\sec\settings.py`
#
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'OPTIONS': {
            'options': '-c search_path=litigations'
        },
        'NAME': 'few_litigations',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

```sh
python manage.py makemigrations
python manage.py migrate
```

To start the crawler, run the following command from the 'sec/mining' directory
```sh
scrapy crawl detail
```

##### The most important files are:
- for actual scrapping `sec\mining\mining\spiders`
- for storing and updating `sec\mining\mining\pipelines.py`

The download delay is currently set to 0.
To add delays between requests, set the maximum number of concurrent requests, or enable autothrottle,
you need to change the mining/mining/settings.py file

Further instructions that are not specific to this project can be found in the documentation of
scrapy (https://scrapy.org/) and django (https://www.djangoproject.com/).

-- dillinger.io was used to make the README.md

