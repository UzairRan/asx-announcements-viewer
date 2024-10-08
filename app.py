# app.py

#imports
import httpx
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import time  

# Function to fetch announcements using httpx and BeautifulSoup
def fetch_announcements(ticker):
    url = f'https://www.asx.com.au/asx/1/company/{ticker}/announcements?count=20&market_sensitive=false'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive'
    }
    try:
        response = httpx.get(url, headers=headers)
        response.raise_for_status()  # Check for HTTP request errors

        # Display response headers and a snippet of the response text for debugging
        st.write("Response Headers:", response.headers)
        st.write("Response Snippet:", response.text[:2000])  # Show first 2000 characters of the response

        # Check if the response is HTML
        if 'text/html' in response.headers.get('Content-Type', ''):
            # Parse HTML to extract announcements
            soup = BeautifulSoup(response.text, 'html.parser')
            announcements = []
            items = soup.find_all('div', class_='col-12 col-md-4 mb-3')
            if not items:
                st.write("No announcements found. Please check the URL or class names.")
            for item in items:
                date = item.find('div', class_='text-muted').text.strip() if item.find('div', class_='text-muted') else 'No Date'
                title = item.find('a', class_='text-dark').text.strip() if item.find('a', class_='text-dark') else 'No Title'
                link = item.find('a', class_='text-dark')['href'] if item.find('a', class_='text-dark') else 'No Link'
                announcements.append({'Date': date, 'Title': title, 'Link': link})
            return pd.DataFrame(announcements)
        else:
            st.write("Unexpected response format. Expected HTML but received something else.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Request failed: {e}")
        return pd.DataFrame()

# List of ticker symbols
tickers = ['AEE', 'REZ', '1AE', '1MC', 'NRZ']

# Streamlit app
st.title('ASX Announcements Viewer')

# Select ticker symbol
selected_ticker = st.selectbox('Select Ticker Symbol', tickers)

# Fetch and display announcements
if st.button('Fetch Announcements'):
    df = fetch_announcements(selected_ticker)
    
    # Introduce a small delay to avoid triggering rate limits
    time.sleep(2)
    
    if not df.empty:
        st.write(f"Recent Announcements for {selected_ticker}:")
        st.dataframe(df)
        
        # Identify "Trading Halt" announcements
        if 'Title' in df.columns and any("Trading Halt" in title for title in df['Title']):
            st.markdown(f"**Ticker {selected_ticker} has a 'Trading Halt' announcement.**")
        else:
            st.markdown(f"**Ticker {selected_ticker} does not have a 'Trading Halt' announcement.**")
    else:
        st.write("No announcements found or there was an error fetching the data.")
