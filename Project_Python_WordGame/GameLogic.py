import random

def scramble_word(word):
    word_list = list(word)
    random.shuffle(word_list)
    return "".join(word_list)

def get_random_word(word_list):
    return random.choice(word_list)
    