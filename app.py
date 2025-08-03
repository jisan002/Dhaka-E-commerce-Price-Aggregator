import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re # For regular expressions to clean price strings

# --- Helper Functions for Scraping (Placeholders - YOU NEED TO FILL THESE IN) ---

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

        # --- IMPORTANT: REPLACE THESE PLACEHOLDERS WITH ACTUAL CSS SELECTORS ---
        # You need to inspect Daraz's website to find the correct selectors.
        # Example: price_element = soup.find('span', class_='price')
        # Example: name_element = soup.find('a', class_='product-name')

        product_card = soup.find('div', class_='gridItem--Yd0sa') # This is a common card class, but might change
        if product_card:
            price_element = product_card.find('span', class_='currency--G_q3k') # Example selector, verify on Daraz
            name_element = product_card.find('div', class_='title--wFj93') # Example selector, verify on Daraz
            link_element = product_card.find('a', class_='product-card-link') # Example selector, verify on Daraz

            price = price_element.text if price_element else "N/A"
            name = name_element.text.strip() if name_element else "N/A"
            product_url = "https://www.daraz.com.bd" + link_element['href'] if link_element and 'href' in link_element.attrs else search_url

            # Clean price string (remove currency symbols, commas, etc.)
            clean_price = float(re.sub(r'[^\d.]', '', price)) if price != "N/A" else None

            return {
                'source': 'Daraz',
                'product_name': name,
                'price': clean_price,
                'url': product_url
            }
        else:
            st.warning("Could not find product on Daraz. Selector might be outdated or product not found.")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Error scraping Daraz: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while scraping Daraz: {e}")
        return None

def scrape_chaldal(product_name):
    """
    Scrapes Chaldal.com for the given product name.
    Returns a dictionary with 'source', 'product_name', 'price', 'url'.
    """
    st.info(f"Searching Chaldal for '{product_name}'...")
    # Chaldal's search URL might be different, verify this
    search_url = f"https://chaldal.com/search/{product_name.replace(' ', '%20')}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # --- IMPORTANT: REPLACE THESE PLACEHOLDERS WITH ACTUAL CSS SELECTORS ---
        # Chaldal often loads content dynamically, so direct requests.get might not get all data.
        # You might need to use Selenium if this doesn't work.
        # Example: price_element = soup.find('span', class_='price-text')
        # Example: name_element = soup.find('div', class_='product-name')

        product_card = soup.find('div', class_='product') # Common product card class, verify
        if product_card:
            price_element = product_card.find('div', class_='price') # Example selector, verify on Chaldal
            name_element = product_card.find('div', class_='name') # Example selector, verify on Chaldal
            link_element = product_card.find('a', class_='product-link') # Example selector, verify on Chaldal

            price = price_element.text if price_element else "N/A"
            name = name_element.text.strip() if name_element else "N/A"
            product_url = "https://chaldal.com" + link_element['href'] if link_element and 'href' in link_element.attrs else search_url

            clean_price = float(re.sub(r'[^\d.]', '', price)) if price != "N/A" else None

            return {
                'source': 'Chaldal',
                'product_name': name,
                'price': clean_price,
                'url': product_url
            }
        else:
            st.warning("Could not find product on Chaldal. Selector might be outdated or product not found.")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Error scraping Chaldal: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while scraping Chaldal: {e}")
        return None

def scrape_swapno(product_name):
    """
    Scrapes Swapno.com.bd for the given product name.
    Returns a dictionary with 'source', 'product_name', 'price', 'url'.
    """
    st.info(f"Searching Swapno for '{product_name}'...")
    # Swapno's search URL might be different, verify this
    search_url = f"https://www.shwapno.com/search?q={product_name.replace(' ', '%20')}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # --- IMPORTANT: REPLACE THESE PLACEHOLDERS WITH ACTUAL CSS SELECTORS ---
        # Example: price_element = soup.find('span', class_='product-price-value')
        # Example: name_element = soup.find('h3', class_='product-title')

        product_card = soup.find('div', class_='product-item') # Common product card class, verify
        if product_card:
            price_element = product_card.find('span', class_='price') # Example selector, verify on Shwapno
            name_element = product_card.find('h2', class_='product-name') # Example selector, verify on Shwapno
            link_element = product_card.find('a', class_='product-link') # Example selector, verify on Shwapno

            price = price_element.text if price_element else "N/A"
            name = name_element.text.strip() if name_element else "N/A"
            product_url = "https://www.shwapno.com" + link_element['href'] if link_element and 'href' in link_element.attrs else search_url

            clean_price = float(re.sub(r'[^\d.]', '', price)) if price != "N/A" else None

            return {
                'source': 'Swapno',
                'product_name': name,
                'price': clean_price,
                'url': product_url
            }
        else:
            st.warning("Could not find product on Swapno. Selector might be outdated or product not found.")
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
    **Important Note:** Web scraping can be fragile. Website structures change frequently,
    which can break the scraping logic. You will need to regularly update the CSS selectors
    within the `scrape_daraz`, `scrape_chaldal`, and `scrape_swapno` functions by
    inspecting the websites' HTML.
    """
)
st.markdown(
    """
    **How to Deploy on Streamlit Cloud (Free):**
    1.  Save this code as `app.py` in a new GitHub repository.
    2.  Create a `requirements.txt` file in the same repository with the following content:
        ```
        streamlit
        requests
        beautifulsoup4
        pandas
        ```
    3.  Go to [Streamlit Cloud](https://share.streamlit.io/).
    4.  Sign in with your GitHub account.
    5.  Click "New app" and select your repository and the `app.py` file.
    6.  Click "Deploy!" and your app will be live and free.
    """
)
