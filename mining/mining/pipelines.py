# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import sys
import django
import spacy

# Adjustment for Local Imports
os.environ['DJANGO_SETTINGS_MODULE'] = 'sec.settings'
django.setup()

# Local Imports
from litigations.models import Litigation, Title, Reference


def clean_string(toClean):
    return toClean.replace("\n", "").replace("\t", "").replace("\xa0", "").replace("\r", "")


class MiningPipeline(object):

    def __init__(self):
        self.count = 0

    def process_item(self, item, spider):

        if item.get("date_modified") is not None:
            print(f'{item.get("date_modified")} FROM {item.get("release_no")}')

        # Check if a litigation exists in the database with the same natural key as the current item
        litigation: Litigation = Litigation.objects.filter(
            release_no=item.get("release_no")).first()

        # if such a litigation does not exist, store it in the database
        if False and litigation is None and spider.name == "detail":
            nlp = spacy.load('en_core_web_sm')

            litigation = Litigation()
            litigation.release_no = item.get("release_no")
            litigation.date = item.get("date")
            litigation.respondents = item.get("respondents")
            litigation.content = item.get("content")
            if item.get("content") is not None:
                doc = nlp(item.get("content"))
                litigation.people = '; '.join(list(set(map(lambda y: clean_string(y.text),
                                                           filter(lambda x: x.label_ == 'PERSON', doc.ents)))))
                litigation.organizations = '; '.join(
                    list(set(map(lambda y: clean_string(y.text), filter(lambda x: x.label_ == 'ORG', doc.ents)))))
                item["people"] = litigation.people
                item["organizations"] = litigation.organizations
            print(item)

            # litigation.save()

            # Titles

            if item.get("h1s") is not None:
                for h1 in item.get("h1s"):
                    if not h1.replace("\r", "").replace("\n", "") == "":
                        title = Title()
                        title.litigation = litigation
                        title.priority = 1
                        title.title_text = h1
                        # title.save()

            if item.get("h2s") is not None:
                for h2 in item.get("h2s"):
                    if not h2.replace("\r", "").replace("\n", "") == "":
                        title = Title()
                        title.litigation = litigation
                        title.priority = 2
                        title.title_text = h2
                        # title.save()

            if item.get("h3s") is not None:
                for h3 in item.get("h3s"):
                    if not h3.replace("\r", "").replace("\n", "") == "":
                        title = Title()
                        title.litigation = litigation
                        title.priority = 3
                        title.title_text = h3
                        # title.save()

            # References

            if item.get("references_names") is not None and item.get("references_urls") is not None:
                for text, url in zip(item.get("references_names"), item.get("references_urls")):
                    reference = Reference()
                    reference.litigation = litigation
                    reference.reference_text = text
                    reference.reference = url
                    # reference.save()

            if item.get("references_sidebar_names") is not None and item.get("references_sidebar_urls") is not None:
                for text, url in zip(item.get("references_sidebar_names"), item.get("references_sidebar_urls")):
                    reference = Reference()
                    reference.litigation = litigation
                    reference.reference_text = text
                    reference.reference = url
                    # reference.save()
