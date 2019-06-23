# Sec Litigation Crawler
 A project for the course Web Programming at FCSE, Skopje
 June, 2019
#### Students invovled, ordered by their index numbers:
  - 161517, Ѓорѓина Цениќ
  - 161528, Филип Маркоски

## Structure
#### scrapy
[Scrapy](https://scrapy.org/) is a free and open-source web-crawling framework written in Python. Originally designed for web scraping, it can also be used to extract data using APIs or as a general-purpose web crawler.

In this project, 'mining' is a scrapy app that crawls 'sec.gov'.
The parsing is done with the LitigationsDetailSpider (mining\mining\spiders\litigations_detail_spider).
The parse_master function collects data (release number, date and respondents) from
'https://www.sec.gov/litigation/litreleases/litrelarchive/litarchiveXXXX.shtml' (where XXXX is the year, 1995<=XXXX<=2018) and sends requests to get additional data (titles, content, references) for each litigation, which are later processed by the
parse_detail function. The parsing functions handle the inconsistencies in the website listed in the issues_checklist.txt file.The pieces of data are stored in item loaders which apply a series of processing functions defined
for each item class in sec\mining\mining\items.py.

The items are written to the database using the process_item function in the MiningPipeline (sec\mining\mining\pipelines.py)
The most important files are:
- for actual scrapping `sec\mining\mining\spiders`
- for storing and updating `sec\mining\mining\pipelines.py`

#### django
[Django](https://www.djangoproject.com/) is a Python-based free and open-source web framework, which follows the model-template-view (MTV) architectural pattern. Django's primary goal is to ease the creation of complex, database-driven websites.

In this project, the django submodule called 'litigations' is used to enable a connection to a PostgreSQL database where the crawled litigations are stored.
Furthermore, we use the [Django REST Framework](https://www.django-rest-framework.org/) to build a REST api. The main building blocks are the models, views, and serializers, which are defined in the corresponding files in the 'sec/litigations' directory. [api root](http://194.149.136.108:8000/)

#### spaCy
[SpaCy](https://spacy.io/) is an open-source software library for advanced Natural Language Processing. It features convolutional neural network models for part-of-speech tagging, dependency parsing and named entity recognition, as well as API improvements around training and updating models, and constructing custom processing pipelines.

In this project, we use spaCy's en_core_web_sm, an English multi-task CNN trained on OntoNotes, to detect the people and organization entities that are mentioned in each litigation. This is done in the pipeline file (`sec\mining\mining\pipelines.py`), before each item is stored in the database.

### How to use
#### Configuring the database in `sec\sec\settings.py`:
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
#### Applying migrations:
```sh
python manage.py makemigrations
python manage.py migrate
```

#### Starting the crawler (from the 'sec/mining' directory)
```sh
scrapy crawl detail
```
#### Starting the server:
```sh
python manage.py runserver
```
#### Crawling settings:
The download delay is currently set to 0.
To add delays between requests, set the maximum number of concurrent requests, or enable autothrottle,
you need to change the mining/mining/settings.py file
```python
# Enable and configure the AutoThrottle extension (disabled by default)
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number o`f requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False
```

Further instructions that are not specific to this project can be found in the documentation of
scrapy (https://scrapy.org/) and django (https://www.djangoproject.com/).

-- dillinger.io was used to make the README.md

