import twilio
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import re
import keys
from twilio.rest import Client

def Send_deals():
    
    #Importing libraries and parsing html

    site_map = 'https://www.edealinfo.com/deals/tech.php'
    response = requests.get(site_map)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    #Finding all <a> tags with class "deal-title" and an href attribute
    deal_links = soup.find_all('a', class_='deal-title', href=True)

    #Appending links found into an empty list to convert to DataFrame
    linklist = []
    for link in deal_links:
        href = link['href']
        linklist.append(href)
        
    #Creating DataFrame using the link list and the title of 'link'
    df = pd.DataFrame({'link' : linklist})
    df['link'] = df['link'].apply(lambda x: urljoin('https://www.edealinfo.com/', x))

    #Here we split the string by the / value and take the last item to get the name of the item
    df['item_name'] = df['link'].str.split('/').str.get(-1).str.replace("-"," ")

    #Getting Prices
    prices = soup.find_all('h3', class_='deal-price text-center hidden-xs')

    #convert to text and clean
    prices = [price.text for price in prices]
    cleaned_prices = []
    for price in prices:
        if re.search('\$', price):
            price = price.replace('$','')
            cleaned_prices.append(price)
        else:
            cleaned_prices.append(price)

    #appending to df
    df['price'] = cleaned_prices

    #Reordering and Cleaning
    new_order = ['item_name','price', 'link']
    df = df[new_order]

    textingdf = df.iloc[:5]

    #Generating Text List
    message_body = f'Hello Ryan, your top tech deals today are:\n\n'

    for index, row in textingdf.iterrows():
        item_name = row['item_name']
        link = row['link']
        price = row['price']
        
        message_body += f"{item_name}\nPrice: ${price}\n\n"
        
    #Twilio Creds
    account_sid = keys.account_sid
    auth_token = keys.auth_token

    # Create a Twilio client
    client = Client(account_sid, auth_token)

    # Send the message
    message = client.messages.create(
        body= message_body,
        from_= keys.from_phone,
        to=keys.to_phone
    )


