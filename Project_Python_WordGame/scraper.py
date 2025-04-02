import requests
from bs4 import BeautifulSoup

def get_words_from_webpage(url, element_selector):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        soup = BeautifulSoup(response.content, "html.parser")
        word_elements = soup.select(element_selector) # CSS selector to extract the words. Inspect the webpage to find the appropriate selector.
        words = [element.text.strip().lower() for element in word_elements if element.text.strip().isalpha() and len(element.text.strip()) > 3] # Filter out non-alphabetic strings and short words
        return words
    except requests.exceptions.RequestException as e:
        print(f"Error fetching webpage: {e}")
        return None
    except AttributeError as e:
      print(f"Error parsing webpage: {e}. Check your CSS selector.")
      return None