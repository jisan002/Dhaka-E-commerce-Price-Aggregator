import streamlit as st
import pandas as pd
import re
import random
import time # For simulating network delay

# --- Simulated Data Functions (For a reliable, ready-to-use demo) ---
# These functions return dummy data to ensure the app works out-of-the-box.
# For real scraping, you would replace the content of these functions
# with actual requests/BeautifulSoup/Selenium logic.

def simulate_scrape_daraz(product_name):
    """Simulates scraping Daraz.com.bd."""
    st.info(f"Simulating search on Daraz for '{product_name}'...")
    time.sleep(random.uniform(0.5, 1.5)) # Simulate network delay
    if "oil" in product_name.lower():
        return {
            'source': 'Daraz',
            'product_name': f"Daraz - {product_name} (5L)",
            'price': round(random.uniform(800, 950), 2),
            'url': "https://www.daraz.com.bd/catalog/?q=" + product_name.replace(' ', '+')
        }
    return None

def simulate_scrape_chaldal(product_name):
    """Simulates scraping Chaldal.com."""
    st.info(f"Simulating search on Chaldal for '{product_name}'...")
    time.sleep(random.uniform(0.7, 1.8)) # Simulate network delay
    if "oil" in product_name.lower():
        return {
            'source': 'Chaldal',
            'product_name': f"Chaldal - {product_name} (5L)",
            'price': round(random.uniform(780, 930), 2),
            'url': "https://chaldal.com/search/" + product_name.replace(' ', '%20')
        }
    return None

def simulate_scrape_swapno(product_name):
    """Simulates scraping Shwapno.com.bd."""
    st.info(f"Simulating search on Swapno for '{product_name}'...")
    time.sleep(random.uniform(0.6, 1.6)) # Simulate network delay
    if "oil" in product_name.lower():
        return {
            'source': 'Swapno',
            'product_name': f"Swapno - {product_name} (5L)",
            'price': round(random.uniform(810, 960), 2),
            'url': "https://www.shwapno.com/search?q=" + product_name.replace(' ', '%20')
        }
    return None

# --- Main Streamlit App ---

st.set_page_config(page_title="Dhaka Price Aggregator", layout="centered")

st.title("🛍️ Dhaka Product Price Aggregator")
st.markdown(
    """
    Enter a product name below, and I'll find its price from various sources
    and show you where you can get the best deal!
    """
)

product_query = st.text_input("Enter Product Name (e.g., 'Soyabin Oil 5L', 'Rice 10kg')", "")

if st.button("Find Best Price"):
    if product_query:
        st.subheader(f"Searching for: **{product_query}**")
        results = []

        # Use simulated scraping functions
        daraz_result = simulate_scrape_daraz(product_query)
        if daraz_result:
            results.append(daraz_result)

        chaldal_result = simulate_scrape_chaldal(product_query)
        if chaldal_result:
            results.append(chaldal_result)

        swapno_result = simulate_scrape_swapno(product_query)
        if swapno_result:
            results.append(swapno_result)

        if results:
            # Convert to DataFrame for easy handling
            df = pd.DataFrame(results)

            # Ensure prices are numeric
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
            st.warning("No results found for the product on Daraz, Chaldal, or Swapno. Please try a different product name.")
    else:
        st.warning("Please enter a product name to search.")

st.markdown("---")
st.info(
    """
    **Important Note on Data:**
    This version uses **simulated data** to ensure the app runs reliably out-of-the-box.
    Actual web scraping is highly prone to breaking due to website changes.

    If you wish to implement **live web scraping**:
    1.  You would need to replace the `simulate_scrape_daraz`, `simulate_scrape_chaldal`,
        and `simulate_scrape_swapno` functions with actual `requests`/`BeautifulSoup`
        and `Selenium` code (similar to previous iterations).
    2.  **For Selenium (e.g., for Chaldal):** You'd need to re-introduce `selenium`
        into `requirements.txt` and ensure `packages.txt` is correctly configured
        for Streamlit Cloud to install `chromedriver` dependencies.
        (e.g., `libglib2.0-0`, `libnss3`, `libgconf-2-4`, `libfontconfig1`).
    """
)
st.markdown(
    """
    **How to Deploy on Streamlit Cloud (Free):**
    1.  **Save this code** as `app.py` in a new GitHub repository.
    2.  **Create a `requirements.txt` file** in the same repository with the following content:
        ```
        streamlit
        pandas
        ```
        *(Note: `requests` and `beautifulsoup4` are not strictly needed for this simulated version, but you can include them if you plan to quickly switch to live scraping later.)*
    3.  **Push both `app.py` and `requirements.txt`** to your GitHub repository.
    4.  Go to [Streamlit Cloud](https://share.streamlit.io/).
    5.  Sign in with your GitHub account.
    6.  Click "New app" and select your repository and the `app.py` file.
    7.  Click "Deploy!" and your app will be live and free.
    """
)
