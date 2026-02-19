# app.py
from flask import Flask, render_template, request, jsonify
import re
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from num2words import num2words

nltk.download('punkt')

app = Flask(__name__)

# ---------------- ENGLISH STEMMER ----------------
english_stemmer = PorterStemmer()

# ---------------- HINDI STEMMER ----------------
def hindi_stem(word):
    suffixes = [
        'ाएंगी','ाएंगे','ाऊंगी','ाऊंगा','ाइयाँ','ाइयों','ाइयां',
        'ाएगी','ाएगा','ाओगी','ाओगे','एंगी','ेंगी','ेंगे',
        'ों','ें','ाएं','ाओं','ियों','ियां',
        'ी','ा','े','ो','ु','ि'
    ]
    for suffix in suffixes:
        if word.endswith(suffix):
            return word[:-len(suffix)]
    return word

# ---------------- TELUGU STEMMER ----------------
def telugu_stem(word):
    suffixes = [
        'లలో','లకు','లని','లను','లతో','ల్లో',
        'లు','ని','ను','కి','లో','గా','తో',
        'ము','ం','ి','ా','ు','ే'
    ]
    for suffix in suffixes:
        if word.endswith(suffix):
            return word[:-len(suffix)]
    return word

# ---------------- TELUGU NUMBER MAP ----------------
telugu_numbers = {
    0:"సున్నా",1:"ఒకటి",2:"రెండు",3:"మూడు",4:"నాలుగు",5:"ఐదు",
    6:"ఆరు",7:"ఏడు",8:"ఎనిమిది",9:"తొమ్మిది",10:"పది",
    11:"పదకొండు",12:"పన్నెండు",13:"పదమూడు",14:"పద్నాలుగు",
    15:"పదిహేను",16:"పదహారు",17:"పదిహేడు",18:"పద్దెనిమిది",
    19:"పంతొమ్మిది",20:"ఇరవై",30:"ముప్పై",40:"నలభై",
    50:"యాభై",60:"అరవై",70:"డెబ్బై",80:"ఎనభై",90:"తొంభై",
    100:"వంద"
}

def telugu_number_to_words(n):
    if n in telugu_numbers:
        return telugu_numbers[n]
    elif n < 100:
        tens = (n // 10) * 10
        ones = n % 10
        return telugu_numbers.get(tens,"") + " " + telugu_numbers.get(ones,"")
    else:
        return str(n)

# ---------------- NUMBER CONVERSION ----------------
def convert_numbers(text, language):
    def replace(match):
        number = int(match.group())
        if language == "en":
            return num2words(number, lang='en')
        elif language == "hi":
            return num2words(number, lang='hi')
        elif language == "te":
            return telugu_number_to_words(number)
        else:
            return match.group()
    return re.sub(r'\d+', replace, text)

# ---------------- NORMALIZATION ----------------
def normalize_text(text, language):

    text = text.lower()
    # Convert numbers to words in the selected language
    text = convert_numbers(text, language)
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Tokenize
    tokens = word_tokenize(text)

    # Apply stemming
    if language == "en":
        stemmed = [english_stemmer.stem(w) for w in tokens]
    elif language == "hi":
        stemmed = [hindi_stem(w) for w in tokens]
    elif language == "te":
        stemmed = [telugu_stem(w) for w in tokens]
    else:
        stemmed = tokens

    return " ".join(stemmed)

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    text = data["text"]
    language = data["language"]

    normalized = normalize_text(text, language)

    return jsonify({"normalized_text": normalized})

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)