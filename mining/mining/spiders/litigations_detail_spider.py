import scrapy
from scrapy.loader import ItemLoader
from mining.items import LitigationItem
import datetime


def remove_characters(s: str, excluded_characters: str) -> str:
    return s.translate(str.maketrans("", "", excluded_characters))


def try_parsing_date(text):
    excluded_characters = ' .,\n\r\t'

    text = text.lower()
    text = remove_characters(text, excluded_characters)
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
            return datetime.datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


class LitigationsDetailSpider(scrapy.Spider):
    name = "detail"

    def start_requests(self):
        current_year = datetime.datetime.now().year

        # The URL for the current_year is different from all the rest
        request_current_year = scrapy.Request(url='https://www.sec.gov/litigation/litreleases.shtml',
                                              callback=self.parse_master)
        request_current_year.meta["year"] = current_year
        yield request_current_year

        # The range() function is exclusive, thus current_year will NOT be considered
        for year in range(1995, current_year):
            if year in [2016, 1999]:
                url = f'https://www.sec.gov/litigation/litreleases/litrelarchive/litarchive{year}.shtml'
                request_master = scrapy.Request(url=url, callback=self.parse_master)
                request_master.meta["year"] = year
                yield request_master

    def parse_master(self, response):
        year = response.meta.get("year")
        item_loader = ItemLoader(item=LitigationItem(), response=response)

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

        rels, dates, resps = item_loader.load_item().values()

        # removing the table headers [not necessary starting from 2018]
        if year < 2018:
            dates.pop(0)
            resps.pop(0)

        # fixing broken release numbers and colspan issue

        if year == 1998 or year == 1999 or year == 2012:
            i = 1

            while i < len(rels):
                code = rels[i].lower()
                if code == "lr-22283":
                    resps.insert(i, "(Intentionally omitted)")

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

        for i in range(0, len(rels)):
            code = rels[i].lower()

            item = LitigationItem()
            item['date'] = try_parsing_date(dates[i])
            item['release_no'] = rels[i]
            item['respondents'] = resps[i]

            # Litigations where the details are intentionally omitted

            if item.get("date") is None:
                path = "//tr[count(@id) = 0]/td[1]/a[text()='{rel_no}']".format(rel_no=rels[i])
                result = response.xpath(path)
                if len(result) != 0:
                    request = scrapy.Request(
                        url='https://www.sec.gov/litigation/litreleases/lr{code}.txt'.format(code=code[3:]),
                        callback=self.parse_detail)
                    request.meta["item"] = item
                    yield request
                else:
                    item["content"] = None
                    item["references_names"] = None
                    item["references_urls"] = None
                    item["references_sidebar_names"] = None
                    item["references_sidebar_urls"] = None
                    yield item

            else:  # for the normal ones

                if year >= 2006:

                    request = scrapy.Request(
                        url='https://www.sec.gov/litigation/litreleases/{year}/lr{code}.htm'
                            .format(year=year,
                                    code=code[3:]),
                        callback=self.parse_detail)
                else:
                    if item.get("date") >= try_parsing_date("May 20, 1999"):
                        request = scrapy.Request(
                            url='https://www.sec.gov/litigation/litreleases/lr{code}.htm'.format(code=code[3:]),
                            callback=self.parse_detail)
                    else:

                        request = scrapy.Request(
                            url='https://www.sec.gov/litigation/litreleases/lr{code}.txt'.format(code=code[3:]),
                            callback=self.parse_detail)

                request.meta["item"] = item
                yield request

    def parse_detail(self, response):
        item = response.meta["item"]  # item is of type Litigation

        item_loader = ItemLoader(item=LitigationItem(), response=response)

        # 1999, LR-16154 is where a major HTML change occurs
        # https://www.sec.gov/litigation/litreleases/lr16154.txt # May 19, 1999
        # https://www.sec.gov/litigation/litreleases/lr16155.htm # May 20, 1999

        if item.get("date") is not None and item.get("date") >= try_parsing_date("May 20, 1999"):
            if item.get("date").year >= 2016:  # new site structure
                item_loader.add_xpath('h1s', '//h1 | //h1/p | //h1/a')
                item_loader.add_xpath('h2s', '//h2 | //h2/p | //h2/a')
                item_loader.add_xpath('h3s', '//h3 | //h3/p | //h3/a')
                item_loader.add_xpath('references_names', '//div[@class="grid_7 alpha"]/p/a/text()')
                item_loader.add_xpath('references_urls', '//div[@class="grid_7 alpha"]/p/a/@href')
                item_loader.add_xpath('references_sidebar_names', '//div[@class="grid_3 omega"]/ul/li/a/text()')
                item_loader.add_xpath('references_sidebar_urls', '//div[@class="grid_3 omega"]/ul/li/a/@href')
                item_loader.add_xpath('content', '//div[@class="grid_7 alpha"]/p')
                item_loader.add_xpath('date_modified', "//*[text()[contains(.,'Modified:')]]/text()")
            else:  # old site structure
                item_loader.add_xpath('h1s', '//h1 | //h1/p | //h1/a')
                item_loader.add_xpath('h2s', '//h2 | //h2/p | //h2/a')
                item_loader.add_xpath('h3s', '//h3 | //h3/p | //h3/a')
                item_loader.add_xpath('references_names',
                                      '//p/a/text() | ((//table)[3]/tr/td[3]/font/table)[position() < last()]//tr/td/a/text()')
                item_loader.add_xpath('references_urls',
                                      '//p/a/@href | ((//table)[3]/tr/td[3]/font/table)[position() < last()]//tr/td/a/@href')
                item_loader.add_xpath('content', '//p | //li')
                item_loader.add_xpath('date_modified', "//*[text()[contains(.,'Modified:')]]/text()")

        else:  # old site structure, litigations with .txt content and no html
            item_loader.add_xpath('content', '//body')

        item_details = item_loader.load_item()
        item.update(item_details)

        return item
