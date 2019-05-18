# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import datetime
from litigations.models import Reference, Litigation, Title
import en_core_web_sm




def try_parsing_date(text):

    text = text.lower().replace(" ", "").replace(".", "").replace(",", "").replace("\n", "").replace("\r", "").replace("\t","")
    text = list(text)
    if len(text) < 8:
        return None
    i = 3
    while i < len(text):
        if text[i].isalpha():
            text.pop(i)
            i -= 1
        i += 1

    text = "".join(text)

    formats = ["%b%d%Y", "%B%d%Y"]
    for fmt in formats:
        try:

            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass


    return None


def clean_string (toClean):
    return toClean.replace("\n", "").replace("\t", "").replace("\xa0","").replace("\r","")

class MiningPipeline(object):

    def __init__(self):
        self.count = 0

    def process_item(self, item, spider):
        litigation: Litigation = Litigation.objects.get(release_no=item.get("release_no"))
        if  spider.name == "detail" and litigation is None:

            nlp = en_core_web_sm.load()
            litigation =  Litigation()
            litigation.release_no = item.get("release_no")
            litigation.date = item.get("date")
            litigation.respondents = item.get("respondents")
            litigation.content = item.get("content")
            if item.get("content") is not None:
                doc = nlp(item.get("content"))
                litigation.people = '; '.join(list(set(map(lambda y: clean_string(y.text),
                                                           filter(lambda x: x.label_ == 'PERSON',doc.ents)))))
                litigation.organizations = '; '.join(list(set(map(lambda y: clean_string(y.text), filter(lambda x: x.label_ == 'ORG', doc.ents)))))
                item["people"]= litigation.people
                item["organizations"]= litigation.organizations
            print (item)
            litigation.save()

            # Titles

            if item.get("h1s") is not None:
                for h1 in item.get("h1s"):
                    if not h1.replace("\r", "").replace("\n", "") == "":
                        title = Title()
                        title.litigation = litigation
                        title.priority = 1
                        title.title_text = h1
                        title.save()

            if item.get("h2s") is not None:
                for h2 in item.get("h2s"):
                    if not h2.replace("\r", "").replace("\n", "") == "":
                        title = Title()
                        title.litigation = litigation
                        title.priority = 2
                        title.title_text = h2
                        title.save()

            if item.get("h3s") is not None:
                for h3 in item.get("h3s"):
                    if not h3.replace("\r", "").replace("\n", "") == "":
                        title = Title()
                        title.litigation = litigation
                        title.priority = 3
                        title.title_text = h3
                        title.save()

            # References

            if item.get("references_names") is not None and item.get("references_urls") is not None:
                for text, url in zip(item.get("references_names"), item.get("references_urls")):
                    reference = Reference()
                    reference.litigation = litigation
                    reference.reference_text = text
                    reference.reference = url
                    reference.save()

            if item.get("references_sidebar_names") is not None and item.get("references_sidebar_urls") is not None:
                for text, url in zip(item.get("references_sidebar_names"), item.get("references_sidebar_urls")):
                    reference = Reference()
                    reference.litigation = litigation
                    reference.reference_text = text
                    reference.reference = url
                    reference.save()





