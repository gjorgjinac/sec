# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import sys
import django
import spacy
import datetime

items_file_path = os.path.abspath(__file__)
mining_subfolder = os.path.dirname(items_file_path)
mining_folder = os.path.dirname(mining_subfolder)
BASE_DIR = os.path.dirname(mining_folder)

print(f'BASE_DIR={BASE_DIR}')

sys.path.append(mining_subfolder)

# Adjustment for Local Imports
os.environ['DJANGO_SETTINGS_MODULE'] = 'sec.settings'
django.setup()

# Local Imports
from litigations.models import Litigation, Title, Reference
from items import LitigationItem

'''en_core_web_sm is an English multi-task CNN trained on OntoNotes. It assigns context-specific token vectors, 
POS tags, dependency parse and named entities.
further reading: https://spacy.io/models/en'''
nlp = spacy.load('en_core_web_sm')


def clean_string(to_clean):
    return to_clean.replace("\n", "").replace("\t", "").replace("\xa0", "").replace("\r", "")


class MiningPipeline(object):

    def __init__(self):
        self.count = 0

    '''After the spider finishes fetching the litigation, it sends it to the pipeline to be written to the database. 
    We also get a reference to the spider to make sure that its name matches the behavior, which is especially
    important when we have multiple spiders running in parallel'''
    def process_item(self, item, spider):

        '''We only want the items that are crawled by the 'detail' spider, and the release_no field is required'''
        if spider.name == "detail" and item.get("release_no") is not None:

            '''Check if a litigation exists in the database with the same natural key as the current item'''
            litigation: Litigation = Litigation.objects.filter(
                release_no=item.get("release_no")).first()

            '''If the item has been modified, we update the date_modified field'''
            if item.get("date_modified") is not None and type(item.get('date_modified')) == list:
                # item.get('date_modified') is a list() for some reason, so a bit of casting is needed
                item['date_modified'] = item.get('date_modified')[0]

            '''If such a litigation does not exist, store it in the database'''
            if litigation is None:
                print('STORING litigation WITH realease_no={} AND content={}'
                      .format(item.get("release_no"), item.get("content")))

                litigation: Litigation = Litigation()
                litigation.release_no = item.get('release_no')
                store_litigation_item(litigation, item)

            elif litigation is not None and item.get("date_modified") is not None:
                # if a newer version of the litigation exists
                date_modified = item.get("date_modified")
                if litigation.date < date_modified:
                    print(f'UPDATING litigation WITH realease_no={item.get("release_no")}')
                    # update that litigation by overwriting all of its fields
                    store_litigation_item(litigation, item)

'''Make necessary checks and store the litigation in the database'''
def store_litigation_item(litigation: Litigation, item: LitigationItem):
    litigation.respondents = item.get("respondents")

    if litigation.respondents == '(Intentionally omitted)':
        litigation.save()
        return

    if item.get("date") is not None:
        litigation.date = item.get("date")

    if item.get("date_modified") is not None:
        litigation.date_modified = item.get("date_modified")

    if item.get("content") is None:
        print(f'INSIDE litigation WITH realease_no={item.get("release_no")} AND content={type(item.get("content"))}')

    if item.get("content") is not None:
        litigation.content = item.get("content")
        '''Apply natural language processing to extract information about the people and organizations
        mentioned in the litigation. We store them in the database in one field with a semicolon separator'''
        doc = nlp(litigation.content)
        litigation.people = '; '.join(list(set(map(lambda y: clean_string(y.text),
                                                   filter(lambda x: x.label_ == 'PERSON', doc.ents)))))
        litigation.organizations = '; '.join(
            list(set(map(lambda y: clean_string(y.text), filter(lambda x: x.label_ == 'ORG', doc.ents)))))
        item["people"] = litigation.people
        item["organizations"] = litigation.organizations
    litigation.save()

    '''Construct a new title object and store it in the database.'''

    if item.get("h1s") is not None:
        for h1 in item.get("h1s"):
            if not h1.replace("\r", "").replace("\n", "") == "":
                title = Title()
                title.litigation = litigation
                title.release_no = litigation.release_no
                title.priority = 1
                title.title_text = h1
                title.save()

    if item.get("h2s") is not None:
        for h2 in item.get("h2s"):
            if not h2.replace("\r", "").replace("\n", "") == "":
                title = Title()
                title.litigation = litigation
                title.release_no = litigation.release_no
                title.priority = 2
                title.title_text = h2
                title.save()

    if item.get("h3s") is not None:
        for h3 in item.get("h3s"):
            if not h3.replace("\r", "").replace("\n", "") == "":
                title = Title()
                title.litigation = litigation
                title.release_no = litigation.release_no
                title.priority = 3
                title.title_text = h3
                title.save()

    '''Construct a new reference object and store it in the database.
    We make no distinction between references extracted from the content and 
    references extracted from the sidebar.
    '''
    if item.get("references_names") is not None and item.get("references_urls") is not None:
        for text, url in zip(item.get("references_names"), item.get("references_urls")):
            reference = Reference()
            reference.litigation = litigation
            reference.release_no = litigation.release_no
            reference.reference_text = text
            reference.reference = url
            reference.save()

    if item.get("references_sidebar_names") is not None and item.get("references_sidebar_urls") is not None:
        for text, url in zip(item.get("references_sidebar_names"), item.get("references_sidebar_urls")):
            reference = Reference()
            reference.litigation = litigation
            reference.release_no = litigation.release_no
            reference.reference_text = text
            reference.reference = url
            reference.save()
