# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pandas as pd
import json

def combine(L):
    results = {}
    for item in L:
        key = (item["Game_Name"])# item["other_position"], item["outfitter"], item["market_values"], item["achievements"])
        if key in results:  # combine them
            Total_components_ = item["Components"] + results[key]["Components"] 
            Total_components= [i for n, i in enumerate(Total_components_) if i not in Total_components_[n + 1:]] #remove duplicates
            
            results[key] = {"Game_Name": item["Game_Name"], "Components": Total_components }#, "transfers": total_transfers}          
        else:  # don't need to combine them
            results[key] = item
    final = list(results.values())
    return final


class GameDebatePipeline:
    def __init__(self):
        self.games = list()

    def process_item(self, item, spider):
        self.games.append(item)
        print (item)
           
    def close_spider(self, spider):
       # print(item)

        #If you want the file in json format, remove the clean_date function from the date_of_birth in the spider
        with open("myjsonfile.json", "wt") as fd:
            json.dump(combine(self.games), fd) 
        #with open('testing', 'w') as myfile:
       #     wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
      #      wr.writerow(combine(self.players))
        #df = pd.DataFrame(combine(self.players))
        #df.to_csv('testing_6.csv', mode = 'a')


