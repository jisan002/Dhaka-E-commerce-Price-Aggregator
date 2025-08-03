import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re # For regular expressions to clean price strings

# For Selenium (Chaldal)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import os # For environment variables, specifically to detect Streamlit Cloud environment

# --- Helper Functions for Scraping ---

def scrape_daraz(product_name):
    """
    Scrapes Daraz.com.bd for the given product name.
    Returns a dictionary with 'source', 'product_name', 'price', 'url'.
    """
    st.info(f"Searching Daraz for '{product_name}'...")
    search_url = f"https://www.daraz.com.bd/catalog/?q={product_name.replace(' ', '+')}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.content, 'html.parser')

        # Selectors for Daraz based on your provided HTML structure
        # Product card: div with class "Bm3ON"
        # Product name: a tag inside a div with class "RfADt"
        # Price: span with class "ooOxS"
        # Link: href attribute of the product name a tag

        # Find the first product card
        product_card = soup.find('div', class_='Bm3ON')
        if product_card:
            name_element = product_card.find('div', class_='RfADt').find('a')
            price_element = product_card.find('span', class_='ooOxS')

            price = price_element.text if price_element else "N/A"
            name = name_element.text.strip() if name_element else "N/A"
            # Daraz links are relative, so prepend the base URL
            product_url = "https:" + name_element['href'] if name_element and 'href' in name_element.attrs else search_url

            # Clean price string (remove currency symbols, commas, etc.)
            clean_price = float(re.sub(r'[^\d.]', '', price.replace('৳', '').replace(',', ''))) if price != "N/A" else None

            return {
                'source': 'Daraz',
                'product_name': name,
                'price': clean_price,
                'url': product_url
            }
        else:
            st.warning("Could not find product on Daraz. Selectors might be outdated or product not found.")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Error scraping Daraz: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while scraping Daraz: {e}")
        return None

def scrape_chaldal(product_name):
    """
    Scrapes Chaldal.com for the given product name using Selenium.
    Returns a dictionary with 'source', 'product_name', 'price', 'url'.
    """
    st.info(f"Searching Chaldal for '{product_name}' using Selenium (this might take a moment)...")
    search_url = f"https://chaldal.com/search/{product_name.replace(' ', '%20')}"

    # Set up Selenium WebDriver options for headless execution
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # Run in headless mode (no browser UI)
    options.add_argument('--no-sandbox') # Required for running in Docker/Linux environments
    options.add_argument('--disable-dev-shm-usage') # Overcomes limited resource problems
    options.add_argument('--disable-gpu') # Applicable for older systems or some cloud environments
    options.add_argument('--window-size=1920,1080') # Set a consistent window size
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    driver = None # Initialize driver to None for finally block
    try:
        # Streamlit Cloud typically has chromedriver at /usr/bin/chromedriver
        # For local development, you'd usually install webdriver_manager or place chromedriver in PATH.
        # This conditional check helps adapt to the environment.
        if "STREAMLIT_SERVER_PORT" in os.environ:
            # Running on Streamlit Cloud
            driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)
        else:
            # Running locally - assuming chromedriver is in PATH or current directory
            # For robust local setup, consider `from webdriver_manager.chrome import ChromeDriverManager; driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)`
            driver = webdriver.Chrome(options=options)

        driver.get(search_url)

        # Wait for the product card to be present. Adjust timeout as needed.
        # Using a more specific selector if possible to ensure the content is loaded.
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.product'))
        )

        # Get the page source after dynamic content has loaded
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Selectors for Chaldal based on your provided HTML structure
        # Product card: div with class "product"
        # Product name: div with class "name"
        # Price: div with class "discountedPrice" or "price" (prefer discounted if available)
        # Link: a tag with class "btnShowDetails"

        product_card = soup.find('div', class_='product')
        if product_card:
            name_element = product_card.find('div', class_='name')
            # Chaldal has both 'discountedPrice' and 'price'. Try to get the active/discounted one first.
            price_element = product_card.find('div', class_='discountedPrice') or product_card.find('div', class_='price')
            link_element = product_card.find('a', class_='btnShowDetails')

            price = price_element.text if price_element else "N/A"
            name = name_element.text.strip() if name_element else "N/A"
            product_url = "https://chaldal.com" + link_element['href'] if link_element and 'href' in link_element.attrs else search_url

            # Clean price string (remove currency symbols, commas, etc.)
            clean_price = float(re.sub(r'[^\d.]', '', price.replace('৳', '').replace(',', ''))) if price != "N/A" else None

            return {
                'source': 'Chaldal',
                'product_name': name,
                'price': clean_price,
                'url': product_url
            }
        else:
            st.warning("Could not find product on Chaldal. Selectors might be outdated or product not found after loading.")
            return None

    except TimeoutException:
        st.error("Chaldal: Page loading timed out. Product data might not have appeared within the given time.")
        return None
    except WebDriverException as e:
        st.error(f"Chaldal: WebDriver error. This often means ChromeDriver is not correctly set up or accessible. Error: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while scraping Chaldal: {e}")
        return None
    finally:
        if driver:
            driver.quit() # Always close the browser to free up resources

def scrape_swapno(product_name):
    """
    Scrapes Swapno.com.bd for the given product name.
    Returns a dictionary with 'source', 'product_name', 'price', 'url'.
    """
    st.info(f"Searching Swapno for '{product_name}'...")
    search_url = f"https://www.shwapno.com/search?q={product_name.replace(' ', '%20')}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Selectors for Swapno based on your provided HTML structure
        # Product card: div with class "product-box"
        # Product name: a tag inside a div with class "product-box-title"
        # Price: span with class "active-price"
        # Link: href attribute of the product-box-gallery a tag

        product_card = soup.find('div', class_='product-box')
        if product_card:
            name_element = product_card.find('div', class_='product-box-title').find('a')
            price_element = product_card.find('span', class_='active-price')
            link_element = product_card.find('a', class_='product-box-gallery') # Link is on the gallery/image wrapper

            price = price_element.text if price_element else "N/A"
            name = name_element.text.strip() if name_element else "N/A"
            product_url = "https://www.shwapno.com" + link_element['href'] if link_element and 'href' in link_element.attrs else search_url

            clean_price = float(re.sub(r'[^\d.]', '', price.replace('৳', '').replace(',', ''))) if price != "N/A" else None

            return {
                'source': 'Swapno',
                'product_name': name,
                'price': clean_price,
                'url': product_url
            }
        else:
            st.warning("Could not find product on Swapno. Selectors might be outdated or product not found.")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Error scraping Swapno: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while scraping Swapno: {e}")
        return None

# --- Main Streamlit App ---

st.set_page_config(page_title="Dhaka Price Aggregator", layout="centered")

st.title("🛍️ Dhaka Product Price Aggregator")
st.markdown(
    """
    Enter a product name below, and I'll try to find its price on Daraz, Chaldal, and Swapno,
    then show you where you can get the best deal!
    """
)

product_query = st.text_input("Enter Product Name (e.g., 'Basmati Rice 5kg', 'Samsung Galaxy S24')", "")

if st.button("Find Best Price"):
    if product_query:
        st.subheader(f"Searching for: **{product_query}**")
        results = []

        # Scrape from each source
        daraz_result = scrape_daraz(product_query)
        if daraz_result:
            results.append(daraz_result)

        chaldal_result = scrape_chaldal(product_query)
        if chaldal_result:
            results.append(chaldal_result)

        swapno_result = scrape_swapno(product_query)
        if swapno_result:
            results.append(swapno_result)

        if results:
            # Convert to DataFrame for easy handling
            df = pd.DataFrame(results)

            # Clean and convert prices to numeric, handling missing values
            df['price_numeric'] = pd.to_numeric(df['price'], errors='coerce')
            df_cleaned = df.dropna(subset=['price_numeric'])

            if not df_cleaned.empty:
                st.subheader("Comparison Results:")
                # Display all found prices
                for index, row in df_cleaned.iterrows():
                    st.write(f"**{row['source']}**: {row['product_name']} - **BDT {row['price_numeric']:.2f}** ([Link]({row['url']}))")

                # Find the best price
                best_deal = df_cleaned.loc[df_cleaned['price_numeric'].idxmin()]
                st.markdown("---")
                st.success(f"🎉 **Best Deal Found!**")
                st.markdown(f"**Product:** {best_deal['product_name']}")
                st.markdown(f"**Price:** **BDT {best_deal['price_numeric']:.2f}**")
                st.markdown(f"**From:** {best_deal['source']} ([Visit Store]({best_deal['url']}))")
            else:
                st.warning("Could not find valid prices for the product on any of the platforms.")
        else:
            st.warning("No results found for the product on Daraz, Chaldal, or Swapno. Please try a different product name or check the website selectors.")
    else:
        st.warning("Please enter a product name to search.")

st.markdown("---")
st.info(
    """
    **Important Note on Web Scraping:**
    Web scraping can be fragile. Website structures change frequently, which can break the scraping logic.
    You will need to regularly update the CSS selectors within the `scrape_daraz`, `scrape_chaldal`,
    and `scrape_swapno` functions by inspecting the websites' HTML.

    **Special Note for Chaldal (Selenium & Deployment):**
    Chaldal uses dynamic content loading, requiring Selenium. The `WebDriver error` you encountered
    (`Status code 127`) on Streamlit Cloud means that the underlying system libraries required by
    `chromedriver` are missing.

    To make this work on Streamlit Cloud, you need to add a `packages.txt` file to your GitHub repository.
    This file tells Streamlit Cloud to install these necessary system packages.
    """
)
st.markdown(
    """
    **How to Deploy on Streamlit Cloud (Free) - Revised Steps:**
    1.  **Save this code** as `app.py` in a new GitHub repository.
    2.  **Create a `requirements.txt` file** in the same repository with the following content:
        ```
        streamlit
        requests
        beautifulsoup4
        pandas
        selenium
        ```
    3.  **Create a `packages.txt` file** in the same repository with the following content:
        ```
        libglib2.0-0
        libnss3
        libgconf-2-4
        libfontconfig1
        ```
        *This `packages.txt` file is crucial for `chromedriver` to run correctly on Streamlit Cloud.*
    4.  **Push both `app.py`, `requirements.txt`, and `packages.txt`** to your GitHub repository.
    5.  Go to [Streamlit Cloud](https://share.streamlit.io/).
    6.  Sign in with your GitHub account.
    7.  Click "New app" and select your repository and the `app.py` file.
    8.  Click "Deploy!" and your app will be live and free.
    """
)
