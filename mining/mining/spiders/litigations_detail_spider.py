import scrapy
from scrapy.loader import ItemLoader
from mining.items import LitigationItem
import datetime

''' a method that removes specified characters from a string
    parameters:
        s-the string from which the characters are supposed to be removed
        excluded_characters-the string containing the characters that are supposed to be removed
    '''
def remove_characters(s: str, excluded_characters: str) -> str:
    return s.translate(str.maketrans("", "", excluded_characters))

''' a method that parses dates with inconsistent formats
    parameters:
        text-the string that is supposed to be parsed as a date'''
def try_parsing_date(text):

    '''extra characters that need to be removed'''
    excluded_characters = ' .,\n\r\t'
    text = text.lower()
    text = remove_characters(text, excluded_characters)

    '''convert the date into a list of characters'''
    text = list(text)

    '''if after the removal of the extra characters, the date does not contain a minimum
    of 8 characters (day,month,year), the date can't be parsed
    '''
    if len(text) < 8:
        return None
    '''remove any extra letters that are not the first 3 characters, which represent the month
    (needed because of the issue in 2003 where some of the dates in september have an extra letter)
    '''
    i = 3
    while i < len(text):
        if text[i].isalpha():
            text.pop(i)
            i -= 1
        i += 1

    text = "".join(text)
    ''' the dates can be in one of two formats:
        %b%d%Y -> Mth d, yyyy
        %B%d%Y -> Month d, yyyy
    '''
    formats = ["%b%d%Y", "%B%d%Y"]

    '''try parsing the date with the previously defined formats'''
    for fmt in formats:
        try:
            return datetime.datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    '''return none if the date could not be parsed with any of the formats'''
    return None


class LitigationsDetailSpider(scrapy.Spider):
    '''This is the name of the spider which is used when we run 'scrapy crawl XXXXX' '''
    name = "detail"

    '''Feeds the crawler with links to pages that are supposed to be crawled'''
    def start_requests(self):
        current_year = datetime.datetime.now().year

        '''We need a separate request for the current year because its URL is not in the same format as the rest
        The constructor of the scrapy Request takes as arguments the url that is supposed to be crawled, and 
        a callback function, which is used to parse the content of the obtained page. 
        '''
        request_current_year = scrapy.Request(url='https://www.sec.gov/litigation/litreleases.shtml',
                                              callback=self.parse_master)
        request_current_year.meta["year"] = current_year
        yield request_current_year

        ''' For every year in the range [1995, current_year), the URLs are in a consistent format'''
        for year in range(1995, current_year):
            if year in [2016, 1999]:
                url = f'https://www.sec.gov/litigation/litreleases/litrelarchive/litarchive{year}.shtml'
                request_master = scrapy.Request(url=url, callback=self.parse_master)
                '''We can add additional data in the request in the form of key-value pairs. 
                We add the year since we need it in order to decide how the content should be parsed'''
                request_master.meta["year"] = year
                yield request_master

    ''' The callback to the first round of requests, which is supposed to extract the release number, date, and 
     the respondents for each litigation'''
    def parse_master(self, response):
        ''' The response contains all of the data we added in the request'''
        year = response.meta.get("year")
        ''' Item Loaders provide the mechanism for populating the items.
        They enable the application of pre-processing and post-processing functions.
        further reading: https://docs.scrapy.org/en/latest/topics/loaders.html'''
        item_loader = ItemLoader(item=LitigationItem(), response=response)

        '''The site's structure is very inconsistent and contains differences that
        can prove rather hard to spot. Make sure you fully understand them before 
        you even think about changing the following code'''
        if year > 2015:
            # new site structure
            item_loader.add_xpath('release_no',
                                  '//tr[count(@id) = 0]/td[1]/a/text() | ' +
                                  '//tr[count(@id) = 0]/td[1]/text()')
            item_loader.add_xpath('date', '//tr[count(@id) = 0]/td[2]')
            item_loader.add_xpath('respondents', '//tr[count(@id) = 0]/td[3]')
        else:
            # old site structure
            item_loader.add_xpath('release_no',
                                  '(//table)[5]/tr[count(@id) = 0]/td[1]/a/text() | ' +
                                  '(//table)[5]/tr[count(@id) = 0]/td[1]/text() ')
            item_loader.add_xpath('date', '(//table)[5]/tr[count(@id) = 0]/td[2]')
            item_loader.add_xpath('respondents', '(//table)[5]/tr[count(@id) = 0]/td[3]')

        '''fetch the release numbers, dates, and respondents of the items stored in the item loader.
        The sequence of function calls load_item().values() returns the fields as 3 lists. It is crucial
         that these lists have the same length and contain a value for each item, because otherwise, 
         the values of the fields for different items may be mixed up'''
        rels, dates, resps = item_loader.load_item().values()

        '''The old site structure does not distinguish between table head and table body, so the values of
         the headers are being parsed as litigation fields and need to be removed [not necessary starting from 2018] '''
        if year < 2018:
            dates.pop(0)
            resps.pop(0)

        '''Some of the release numbers in the litigations from 1998,1999 and 2012
         are not in the expected format: 'LR-XXXXX' '''

        if year == 1998 or year == 1999 or year == 2012:
            i = 1

            while i < len(rels):
                code = rels[i].lower()
                '''If a litigation does not have a respondent specified, the field usually contains an explanation
                in the form of '(Intentionally omitted)'. When such an explanation is not present, the order of the 
                respondents, release numbers and years is disrupted, so we have to make sure every item contains a value
                for each field'''
                if code == "lr-22283":
                    resps.insert(i, "(Intentionally omitted)")

                '''extracting the numbers from each litigation's release number and establishing a consistent format'''
                if len(code) < 8:
                    numbers = []
                    for codechar in code:
                        if codechar.isdigit():
                            numbers.append(codechar)
                    if len(numbers) == 5:
                        rels[i] = "lr-" + "".join(numbers)
                    else:
                        rels.pop(i)
                        i -= 1
                i += 1

        # print("--------------\nYEAR:{0}\nRELNS:{1}\nDATES:{2}\nRESPS:{3}\n".format(year, len(rels), len(dates),len(resps)))

        # if len(rels) != len(dates) or len(rels) != len(resps) or len(resps) != len(dates):
        # print("ERROR IN YEAR: {0}".format(year))

        '''Constructing an instance of LitigationItem with the values obtained from the item loader'''
        for i in range(0, len(rels)):
            code = rels[i].lower()

            item = LitigationItem()
            item['date'] = try_parsing_date(dates[i])
            item['release_no'] = rels[i]
            item['respondents'] = resps[i]

            # Litigations where the details are intentionally omitted

            if item.get("date") is None:
                '''If the date is missing, check whether the litigation entry contains a link to the 
                details page'''
                path = "//tr[count(@id) = 0]/td[1]/a[text()='{rel_no}']".format(rel_no=rels[i])
                result = response.xpath(path)
                '''If there is a link to the details page, send another request to the details page to fetch the content'''
                if len(result) != 0:
                    request = scrapy.Request(
                        url='https://www.sec.gov/litigation/litreleases/lr{code}.txt'.format(code=code[3:]),
                        callback=self.parse_detail)
                    '''We add the item with the data we have obtained so far in the request, so that we can continue
                    building it and add the new data obtained from the details page'''
                    request.meta["item"] = item
                    yield request

                else:
                    '''If there is no link to the details page, populate the additional fields with None '''
                    item["content"] = None
                    item["references_names"] = None
                    item["references_urls"] = None
                    item["references_sidebar_names"] = None
                    item["references_sidebar_urls"] = None
                    yield item

            else:
                '''If the date is present, we need to send a request to fetch the content from the details page.
                 To do that, we need to check the year, because after 2006, the URL format of the details pages changes.
                 We omit the first 3 characters of the code because the code is in format LR-XXXXX, and we only need the numbers XXXXX'''
                if year >= 2006:
                    request = scrapy.Request(
                        url='https://www.sec.gov/litigation/litreleases/{year}/lr{code}.htm'
                            .format(year=year,
                                    code=code[3:]),
                        callback=self.parse_detail)
                else:
                    '''In the old site structure (before May 20, 1999), the details about the litigations are stored 
                    in a txt format rather than html, so we need a different URL in order to fetch them'''
                    if item.get("date") >= try_parsing_date("May 20, 1999"):
                        request = scrapy.Request(
                            url='https://www.sec.gov/litigation/litreleases/lr{code}.htm'.format(code=code[3:]),
                            callback=self.parse_detail)
                    else:
                        request = scrapy.Request(
                            url='https://www.sec.gov/litigation/litreleases/lr{code}.txt'.format(code=code[3:]),
                            callback=self.parse_detail)
                '''We add the item with the data we have obtained so far in the request, so that we can continue
                building it and add the new data obtained from the details page'''
                request.meta["item"] = item
                yield request

    ''' The callback to the second round of requests, which is supposed to extract the content, titles, and references for each litigation'''
    def parse_detail(self, response):

        '''We extract the item which we previously added in the request. The fields for the release number, date, and respondents
        have already been populated'''
        item = response.meta["item"]  # item is of type Litigation

        '''We construct a new item loader that is supposed to collect the content, titles and references.
        We will later on merge the item constructed with this item loader with the one we constructed in the
        parse_master function'''
        item_loader = ItemLoader(item=LitigationItem(), response=response)

        ''' 1999, LR-16154 is where the shift from txt format to html format occurs
        https://www.sec.gov/litigation/litreleases/lr16154.txt # May 19, 1999
        https://www.sec.gov/litigation/litreleases/lr16155.htm # May 20, 1999
        '''
        if item.get("date") is not None and item.get("date") >= try_parsing_date("May 20, 1999"):

            if item.get("date").year > 2016:

                '''
                The data is being collected by extracting it from a specified XPath location, using the add_xpath() method. 
                Alternatively, add_css() or add_value() can be used.
                Further reading: https://docs.scrapy.org/en/latest/topics/loaders.html#item-loader-context
                The tags of the litigation titles follow no convention. They are randomly placed in 
                h1, h2, or h3 tags, and can contain nested anchor or paragraph tags.
                '''
                item_loader.add_xpath('h1s', '//h1 | //h1/p | //h1/a')
                item_loader.add_xpath('h2s', '//h2 | //h2/p | //h2/a')
                item_loader.add_xpath('h3s', '//h3 | //h3/p | //h3/a')

                '''In 2016, there is a change in the site's structure: The references which up till
                that point were only included in the text, can now also be added in the sidebar. 
                Furthermore, these references are not the same and their placement follows no apparent
                rule, so we have to fetch both of them separately'''

                item_loader.add_xpath('references_names', '//div[@class="grid_7 alpha"]/p/a/text()')
                item_loader.add_xpath('references_urls', '//div[@class="grid_7 alpha"]/p/a/@href')
                item_loader.add_xpath('references_sidebar_names', '//div[@class="grid_3 omega"]/ul/li/a/text()')
                item_loader.add_xpath('references_sidebar_urls', '//div[@class="grid_3 omega"]/ul/li/a/@href')
                item_loader.add_xpath('content', '//div[@class="grid_7 alpha"]/p')

                '''The date of modification is later on used to check whether an existing litigation needs to be updated in the database'''
                item_loader.add_xpath('date_modified', "//*[text()[contains(.,'Modified:')]]/text()")
            else:  # old site structure
                item_loader.add_xpath('h1s', '//h1 | //h1/p | //h1/a')
                item_loader.add_xpath('h2s', '//h2 | //h2/p | //h2/a')
                item_loader.add_xpath('h3s', '//h3 | //h3/p | //h3/a')
                '''Before 2016, there are no references placed in the sidebars, so we do not need to check for them'''
                item_loader.add_xpath('references_names',
                                      '//p/a/text() | ((//table)[3]/tr/td[3]/font/table)[position() < last()]//tr/td/a/text()')
                item_loader.add_xpath('references_urls',
                                      '//p/a/@href | ((//table)[3]/tr/td[3]/font/table)[position() < last()]//tr/td/a/@href')
                item_loader.add_xpath('content', '//p | //li')
                item_loader.add_xpath('date_modified', "//*[text()[contains(.,'Modified:')]]/text()")

        else:
            '''This last check is used for the older litigations in txt format.
            Since we can't parse the content in a txt file, we put the whole thing in the content field'''
            item_loader.add_xpath('content', '//body')


        item_details = item_loader.load_item()
        '''The item_details object now contains the content, titles, and references, while item contains
        the release number, date, and respondents. We need to merge them before we send the item to the pipeline '''
        item.update(item_details)

        return item
