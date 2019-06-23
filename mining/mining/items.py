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

'''Special parsing for the extracted date of modification'''
def filter_date_modified(value):
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

'''Convert relative to absulte urls'''
def relative_to_absolute_url(value):
    if value[0] == '/':
        return "https://www.sec.gov{0}".format(value)
    else:
        return value


def filter_respondents(value):
    result = value.strip('\n').strip('\r').strip(' ').strip(';').replace("\r\n", "")
    result = result.split("See also")[0]
    if len(result) > 2:
        return result


def filter_releasenos(value):
    result = value.replace("\r", "").replace("\n", "").replace(" ", "").replace("\t", "")
    if len(result) > 0:
        return result
    else:
        return None

'''Filter out the fields with no useful content'''
def filter_empty(value):
    result = value.replace("\r", "").replace("\n", "").replace(" ", "").replace("\t", "")
    if len(result) > 0:
        return value
    else:
        return None


def fix_unicode(value):
    return value.encode('utf-8')

'''The functions of the following classes are used by the item loader to preprocess the 
values before they are sent to the pipeline. 
An Item Loader contains one input processor and one output processor for each (item) field. 
The input processor processes the extracted data as soon as it’s received  and the result 
of the input processor is collected and kept inside the ItemLoader. After collecting all data,
the ItemLoader.load_item() method is called to populate and get the populated Item object. 
That’s when the output processor is called with the data previously collected (and processed using the input processor). 
The result of the output processor is the final value that gets assigned to the item. 
further reading: https://docs.scrapy.org/en/latest/topics/loaders.html#input-and-output-processors
 '''
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
        input_processor=MapCompose(remove_tags, filter_date_modified)
    )

    references_names = scrapy.Field()
    references_urls = scrapy.Field(input_processor=MapCompose(relative_to_absolute_url))
    references_sidebar_names = scrapy.Field()
    references_sidebar_urls = scrapy.Field(input_processor=MapCompose(relative_to_absolute_url))


class ReferenceItem(scrapy.Item):
    litigation = scrapy.Field()
    reference = scrapy.Field()
    reference_text = scrapy.Field()
