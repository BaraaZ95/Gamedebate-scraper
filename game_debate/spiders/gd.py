import scrapy
from ..items import transform_dict
from scrapy import signals


class GdSpider(scrapy.Spider):
    name = 'gd'
    allowed_domains = ['www.game-debate.com']
    start_urls = [f'https://www.game-debate.com/games?year={year}' for year in range(2000, 2024)] 
    handle_httpstatus_list = range(300,405)
    
    #Append all failed urls in a list to retry them separately later
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.failed_urls = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(GdSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.handle_spider_closed, signals.spider_closed)
        return spider

    def parse(self, response):
        urls = response.css('div[class="games-list-table"] > table > tbody > tr > td> a::attr(href)').getall()
        urls = [url.replace(' ', '%20') for url in urls]
        urls = ['https://www.game-debate.com' + url for url in urls]
        for url in urls:
            yield scrapy.Request(url, callback= self.parse_game)
    
    async def parse_game(self, response):
        if response.status in [404,429]: # response fails, append to a list to retry it again later 
            self.crawler.stats.inc_value('failed_url_count')
            self.failed_urls.append(response.url)
        else:
            Game = dict()
            Game['Name'] = response.css('h2::text').get().replace('System Requirements', '').strip()           
            Game['Release_Date'] = response.css('div[class="game-page-right-col"] > div [class="game-release-date"]> p::text').getall()[1].strip()     
            requiremnts = response.css('div[class="system-requirements-body"]')    
            rows = requiremnts.css('tr')
            values_columns = list() #Used to store RAM, VRAM, OS, HDD Space and DirectX values. CPU and GPU will be scraped separately 
            cpus_gpus = list()   
              
            for row in rows: # convert every row's values into a list for both minimum and recommended requirements to be cleaned later            
                values_columns.append([i.strip() for i in row.xpath('td//text()').getall()])
                values = row.css('td> div>a::text').getall()
                values = [i.strip() for i in values if i]
                urls = row.css('td> div>a::attr(href)').getall()
                new_urls = []
                for part in urls:
                    if 'cpu' in part:
                        new_urls.append({"CPU":part})
                    elif 'graphics' in part:
                        new_urls.append({"GPU":part})
                cpus_gpus.append({"Min": dict(zip(values[0:1],new_urls[0:1]))})
                cpus_gpus.append({"Recommended": dict(zip(values[1:],new_urls[1:]))})     
            cpus_gpus = [i for i in cpus_gpus if list(i.values())[0]]
                    
            for value in values_columns:
                if len(value[0]) > 0:
                    new_value = [i for i in value if i!= '' if i!=  '0' ]  
                    Game .update({new_value[0]:new_value[1:3]}) # the first element is the row's title. The other values are the minimum and recommended values
            
            cpus_gpus = [transform_dict(value) for value in cpus_gpus]
            components = []       
            for part in cpus_gpus: 
                req =  scrapy.Request(part['url'], callback= self.parse_part_info ,cb_kwargs= {"part": part})
                res =  await self.crawler.engine.download(req, self)         
                components.append(self.parse_part_info(res, part = part))
            Game['Components'] = components
            
            #Processor and Graphics card elements will be edited seperately data procesing
            Game.pop('Processor', None)  
            Game.pop('Graphics Card', None) 
            yield Game
    
    def parse_part_info(self, response, part):
        info = {'Name': response.css('div[class="hardware-title-text"]::text').get().strip()}
        boxes =  response.css('div[class="hardware-info-box"]')
        rows = boxes.css('div[class="hardware-info-row"]')
        vals_t = []
        keys_t = []
        for row in rows:
            key = row.css('div[class="hardware-info-title"]>span::text').get(default = '') 
            if len(key)<1:
                key = row.css('div[class="hardware-info-title"]>div>span::text').get(default = '')
            if len(key)<1:
                key = row.css('div[class="hardware-info-title"]>a::text').get()
            keys_t.append(key)
            value =  row.css('div[class="hardware-info-value"]>span::text').get(default = '') #values can have different locations
            if len(value) <2:
                value = row.css('div[class="hardware-info-value"]>span>svg::attr(class)').get(default = '')
            if len(value) <2:
                value =  row.css('div[class="hardware-info-value"]>div>span>svg::attr(class)').get(default = '')
            if len(value)< 1: #GD RATING is the only value that can have single digit
                value =  row.css('div[class="hardware-info-value"]>div>svg>g>text::text').get()
            vals_t.append(value)
        #keys_t = [i.replace('\n', '') for i in keys_t if i]
        #vals_t = [i.replace('\n', '') for i in vals_t if i]
        info.update(dict(zip(keys_t, vals_t)))   
        info = {k.replace('\n', ''):v.replace('\n', '') for k,v in info.items() if v}  
        part.update(info)        
        part.pop('url', None)
        return part
    
    def handle_spider_closed(self, reason):
        self.crawler.stats.set_value('failed_urls', ', '.join(self.failed_urls))

    def process_exception(self, response, exception, spider):
        ex_class = "%s.%s" % (exception.__class__.__module__, exception.__class__.__name__)
        self.crawler.stats.inc_value('downloader/exception_count', spider=spider)
        self.crawler.stats.inc_value('downloader/exception_type_count/%s' % ex_class, spider=spider)
        
        
        
        
                
                
                
            
        
                
            
        
            
        
            
