# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import os
import datetime
import scrapy
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags


def filter_date_modification(value):
    if type(value) is not str:
        return None

    result = value.replace("Modified", "")
    excluded_characters = ' .,:\n\r\t\\/'
    result = result.translate(str.maketrans("", "", excluded_characters))
    formats = ["%b%d%Y", "%B%d%Y", '%m%d%Y']
    for fmt in formats:
        try:
            result = datetime.datetime.strptime(result, fmt).date()
            print(f'date_modified={result}')
            return result
        except ValueError:
            pass
    print(f'date_modified={result}')
    return result


def relative_to_absolute_url(value):
    if value[0] == '/':
        return "https://www.sec.gov{0}".format(value)
    else:
        return value


def filter_respondents(value):
    result = value.strip('\n').strip('\r').strip(' ').strip(';').replace("\r\n", "")
    result = result.split("See also")[0]
    if len(result) > 2:
        # result = "{word}-[{length}]".format(word=result, length=len(result))
        return result


def filter_releasenos(value):
    result = value.replace("\r", "").replace("\n", "").replace(" ", "").replace("\t", "")
    if len(result) > 0:
        return result
    else:
        return None


def filter_empty(value):
    result = value.replace("\r", "").replace("\n", "").replace(" ", "").replace("\t", "")
    if len(result) > 0:
        return value
    else:
        return None


def fix_unicode(value):
    return value.encode('utf-8')


class LitigationItem(scrapy.Item):
    people = scrapy.Field()
    organizations = scrapy.Field()

    release_no = scrapy.Field(
        input_processor=MapCompose(remove_tags, filter_releasenos)
    )
    date = scrapy.Field(
        input_processor=MapCompose(remove_tags)
    )
    respondents = scrapy.Field(
        input_processor=MapCompose(remove_tags, filter_respondents)
    )
    content = scrapy.Field(
        input_processor=MapCompose(remove_tags, filter_empty),
        output_processor=Join("\n")
    )

    h1s = scrapy.Field(
        input_processor=MapCompose(remove_tags)
    )
    h2s = scrapy.Field(
        input_processor=MapCompose(remove_tags)
    )
    h3s = scrapy.Field(
        input_processor=MapCompose(remove_tags)
    )
    h4s = scrapy.Field(
        input_processor=MapCompose(remove_tags)
    )

    date_modified = scrapy.Field(
        input_processor=MapCompose(remove_tags, filter_date_modification)
    )

    references_names = scrapy.Field()
    references_urls = scrapy.Field(input_processor=MapCompose(relative_to_absolute_url))
    references_sidebar_names = scrapy.Field()
    references_sidebar_urls = scrapy.Field(input_processor=MapCompose(relative_to_absolute_url))


class ReferenceItem(scrapy.Item):
    litigation = scrapy.Field()
    reference = scrapy.Field()
    reference_text = scrapy.Field()
