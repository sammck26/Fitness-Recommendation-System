import scrapy  
from time import *
from random import randint
from scrapy.crawler import CrawlerProcess
import urllib.parse # used to get location
import requests
import pickle

class MySpider(scrapy.Spider):
    name = "my_spider"
    start_urls = ["https://nrpt.co.uk/find/index.htm"]
    def __init__(self):
        self.urls = [] # this si the specific profile urls
        self.location_urls = [] # this is the urls that contain the lists of pts
        self.number_of_yeilded_profiles = 0
        self.the_stuff = {} # this is the dict that will store all the info

    
    
        
        
                           
    custom_settings = {
        'DOWNLOAD_DELAY': randint(2, 4),  # Delay between requests
        'ROBOTSTXT_OBEY': True,  
        #'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',  # To avoid being blocked
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }
    
    def parse(self, response):
        self.logger.info("got inside the URL function")
       
        #print("the respomse", response) 
        #print("the a tag", response.css('a.wtrk-click'))
        locations = response.css('select[id="courses-where"] option::text').getall() # all locatiosn stored on pt site

        #print("the locations", locations)


        headers = { #custom settings only apply to scrapy API and geo requires emial and user name ot use website

        'User-Agent': 'MyScrapyApp/1.0 (sammckibben60@gmil.com@example.com)'
        }

        # for location in locations: # iterates over all locations

        #     url = 'https://nominatim.openstreetmap.org/search?q=' + urllib.parse.quote(location) +'&format=json' # url to get lat and long
        #     # print("the url", url)   
        #     geo_response = requests.get(url, headers= headers).json() #searches for loactiosn lat and long using geo appi

        #     # print(f"Location: {location}"),
        #     # print(geo_response[0]["lat"]),
        #     # print(geo_response[0]["lon"]),
        #     print("self.locations_lat_long", self.locations_lat_long)
        #     try:
        #         self.locations_lat_long[location] = (geo_response[0]["lat"], geo_response[0]["lon"]) # stores tehblat and long in a dict with the location name as a key
        #     except Exception as e: # skips api calls that retunr null
        #         print(f"skipping {location} no lat and long found in geo respinse") 
        #         continue

        self.location_urls = [f"https://nrpt.co.uk/profiles/trainers/searchresults.htm?query={location}&type=location&page=" + str(i)
        for location in locations # this craetes a list of all the urls that contain the lists of pts
            for i in range(1,11)
        ]
        yield{
            'urls': self.location_urls
        }
        
        yield from self.following_location_urls(response) # calls the following urls function
        #yield from self.following_location_urls(response,urls) # calls the following urls function
        

    def following_location_urls(self,response): # follows all the location urls and calls the start_requests function
        print("got insoide the following_location_urls function")
        #print("all the the urls", urls)
        self.urls = [] # reset the urls
        for url in self.location_urls: # goe sthrough the list and applys the profile urls function 
            #print("the urls", url)
            
            try:
               
                yield response.follow(url, callback=self.profile_urls)

                
            except Exception as e: #this will skip a url that most likey doesn't exist 
                #print(f"Error with {url} error {e} is type {type(self.location_urls)}")
                
                continue
            
        
         # follows all the urls and calls the start_requests function
       
    def profile_urls(self,response): # goes through each page of pts and extracts the urls directly to their profiles
        base_url = "https://nrpt.co.uk/" #append sto the exctacted url
        print("got inside the profile_urls function")
        print("the resposne in the url function", response)
        
        for links in response.css('a.wtrk-click'): # loops over the claaa that contaoins all  te profile urls
            
            url =  links.attrib['href'] # extracts the url
            actual_url = base_url + url
            if actual_url not in self.urls: # url was repeating so if we dont alrreday ahve it extract it
                self.logger.info(f"Extracted URL: {url}")
                self.logger.info("got inside the loop") 
                
                self.urls.append(actual_url)
                print(actual_url)
                print("testing")
            else:
                print("url already exists")
                continue
        print("the urls", self.urls)
        yield{
            'urls': self.urls 
        }
        yield from self.get_details(response)
        
       
    
    def parse_details(self, response): # goes through profile and hgarbs info
        self.logger.info("got inside the parse_details function")
        self.logger.info(f"Scraping profile page: {response.url}") # this logs which prfileis currrenly being crawled as scrapy processes requests in fastest order
        for details in response.css('div.trainers-content'): # class that contains the details
            self.logger.info("got inside the loop")
            # yield{
            #     'quote': details.css('div.about-me p::text').get(),
            #     'about and testimonals':[ text.replace("\xa0","") for text in details.css('div[class="small-12 columns"] p::text').getall()] , #\xa0
                
            #     'qualifications_expertise': details.css('div.row li::text').getall(),
                
            # }
            self.number_of_yeilded_profiles = self.number_of_yeilded_profiles + 1 # this is to count the number of scrtaped profiles
            name = details.css('div.small-12.medium-9 h1::text').get()
            self.the_stuff[f"Profile {name} profile number {self.number_of_yeilded_profiles}"] = {'quote':[text.replace("\xa0","") for text in details.css('div.about-me p::text').getall()],
                                                                                                  'about and testimonals':[ text.replace("\xa0","") for text in details.css('div[class="small-12 columns"] p::text').getall()] , 
                                                                                                  'qualifications_expertise': details.css('div.row li::text').getall()} # addinfg the details to a dict
            #print(self.the_stuff)

        
            self.logger.info(f"Finished profile #{self.number_of_yeilded_profiles}: {name}") #scrapy is weird so checkog it finshes prfiles beofre contuniing
            

        

    def get_details(self, response): #goes through each url
        self.logger.info("got inside the get_details function")
        print("the urls", self.urls)
        for urls in self.urls:
            #print("processing url",urls)
            #yield response.follow(urls, callback=self.parse_details) # calls the pars_detasuls function ona speicifc profoel
            self.logger.info(f"Yielding profile URL: {urls}")
            yield scrapy.Request(urls, callback=self.parse_details, dont_filter=True)
        
       #once that abtch of urls is prcessed move to th next
        yield from self.following_location_urls(response) # calls the following location urls functions
        
            
    def closed(self, reason): # this should run when we haev scarped all the profiles
        print("have finsihed urls")
        geeky_file = open('nrpt_trainers', 'wb')  #creates a pickle file
        print("the stuff", self.the_stuff)
        pickle.dump(self.the_stuff, geeky_file) 
        geeky_file.close() 
        self.crawler.engine.close_spider(self, reason=reason) #  stops the slider fomr running
process = CrawlerProcess(settings={ #allows me ot run code inside of vs code
    
    })    

process.crawl(MySpider)
process.start()
       


                


