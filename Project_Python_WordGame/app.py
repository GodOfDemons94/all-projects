from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import scraper
import GameLogic

app = Flask(__name__)

# Initialize outside the route
current_word = None
scrambled_word = None

# Example usage (you'll need to find a suitable website and selector):
word_list_url = "https://www.eaglecreek.com/blogs/articles/what-pack-ultimate-travel-packing-checklist"
word_elements_selector = "ul li"
words = scraper.get_words_from_webpage(word_list_url, word_elements_selector)

if words is None:
    print("Could not retrieve words. Check the URL and Selector")
    exit()

@app.route("/", methods=["GET", "POST"])
def index():
    global current_word, scrambled_word
    if not words: # Handles the case where words is None or an empty list
        return "Error: No words available. Check the word source and scraping process."
    
    if current_word is None: # Generate the first word only if it's None.
        current_word = GameLogic.get_random_word(words)
        scrambled_word = GameLogic.scramble_word(current_word)

    if request.method == "POST":
        user_answer = request.form.get("user_answer").lower()
        if user_answer == current_word:
            result = "Correct!"
            current_word = GameLogic.get_random_word(words)
            scrambled_word = GameLogic.scramble_word(current_word)
        else:
            result = "Incorrect. Try again!"
        return render_template("index.html", scrambled_word=scrambled_word, result=result, current_word=current_word)
    else:
        current_word = GameLogic.get_random_word(words)
        scrambled_word = GameLogic.scramble_word(current_word)
        return render_template("index.html", scrambled_word=scrambled_word, result="", current_word=current_word)


if __name__ == "__main__":
    app.run(debug=True)  # debug=True for automatic reloading during development