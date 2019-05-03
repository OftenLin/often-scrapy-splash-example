from scrapy import Field as field
from scrapy import Item


class FscFinanicalDictionaryItem(Item):
    # define the fields for your item here like:
    order_num = field()
    category = field()
    chinese = field()
    english = field()
    source = field()
