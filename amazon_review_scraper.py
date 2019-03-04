from lxml import html
from json import dump,loads
from requests import get
import requests
import json
from re import sub
from dateutil import parser as dateparser
from time import sleep
requests.packages.urllib3.disable_warnings()


def ParseReviews(asin):
     amazon_url  = 'http://www.amazon.in/dp/'+asin
     headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.53 Safari/525.19'}
     for i in range(5):
        response = get(amazon_url, headers = headers, verify=False, timeout=30)
        if response.status_code == 404:
            return {"url": amazon_url, "error": "page not found"}
        if response.status_code != 200:
            continue

     cleaned_response = response.text.replace('\x00', '')
     parser = html.fromstring(cleaned_response)
     XPATH_AGGREGATE_RATING = '//table[@id="histogramTable"]//tr'
     XPATH_REVIEW_PATH = '//a[@id="acrCustomerReviewLink"]'
     
     total_ratings  = parser.xpath(XPATH_AGGREGATE_RATING)
     reviews_link = parser.xpath(XPATH_REVIEW_PATH)
     ratings_dict = {}
     reviews_list = []
     
     # Grabing the rating  section in product page
     for ratings in total_ratings:
         extracted_rating = ratings.xpath('./td//a//text()')
         if extracted_rating:
             rating_key = extracted_rating[0] 
             raw_raing_value = extracted_rating[1]
             rating_value = raw_raing_value
             if rating_key:
                 ratings_dict.update({rating_key: rating_value})
                 
     for review_link in reviews_link:
            review_page_url = 'http://www.amazon.in/' + review_link.attrib['href']

     last_page = False
     while not last_page:
         print(review_page_url)
         response = get(review_page_url, headers = headers, verify=False, timeout=30)
         cleaned_response = response.text.replace('\x00', '')
         parser = html.fromstring(cleaned_response)
         
         XPATH_NEXT_PAGE = '//li[@class="a-last"]/a'
         XPATH_LAST_PAGE = '//li[@class="a-disabled a-last"]'
         XPATH_REVIEWS = '//div[@data-hook="review"]'

         last_page_reached = parser.xpath(XPATH_LAST_PAGE)
         reviews = parser.xpath(XPATH_REVIEWS)
         print("parsed ")
             #Individual reviews
         if reviews:
             for review in reviews:
                 XPATH_REVIEW_BODY = './/span[@data-hook="review-body"]//text()'
                 XPATH_REVIEW_HEADER = './/span[@class="cr-original-review-content"]//text()'
                 XPATH_REVIEW_POSTED_DATE = './/span[@data-hook="review-date"]//text()'

                 raw_review_posted_date = review.xpath(XPATH_REVIEW_POSTED_DATE)
                 try:
                     review_posted_date = dateparser.parse(''.join(raw_review_posted_date)).strftime('%d %b %Y')
                 except:
                     review_posted_date = None
                     
                 review_header = review.xpath(XPATH_REVIEW_HEADER)
                 review_body = review.xpath(XPATH_REVIEW_BODY)
                 review_dict = {
                                'review_body': review_body,
                                'review_posted_date': review_posted_date,
                                'review_title': review_header,
                               }
                 reviews_list.append(review_dict)
                 
         reviews_link = parser.xpath(XPATH_NEXT_PAGE)
         for review_link in reviews_link:
             review_page_url = 'http://www.amazon.in/' + review_link.attrib['href']
         if last_page_reached:
             last_page = True

     data = {
                 'ratings': ratings_dict,
                 'review_count': len(reviews_list),
                 'reviews': reviews_list
            }
     return data
      
def ReadAsin():
    AsinList = ['B07J37JZQM']
    extracted_data = []
    for asin in AsinList:
        print("Downloading and processing page http://www.amazon.in/dp/" + asin)
        extracted_data.append(ParseReviews(asin))
        sleep(5)
    f = open('data1.json', 'w')
    dump(extracted_data, f, indent=4)
    f.close()

if __name__ == '__main__':
    ReadAsin()
