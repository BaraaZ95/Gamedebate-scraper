# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

def transform_dict(item):
    item_spec = list(item.keys())[0]
    item_dict = list(item.values())[0]
    item_name = list(item_dict.keys())[0]
    item_type = list(list(item_dict.values())[0].keys())[0]
    item_url = list(item_dict.values())[0][item_type]
    item_url =  'https://www.game-debate.com' +  item_url.replace(' ','%20')
    
    return {"Name": item_name, "Spec": item_spec, "url": item_url, "Type": item_type}
    
    
    
    
    
    
    
    
class GameDebateItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
