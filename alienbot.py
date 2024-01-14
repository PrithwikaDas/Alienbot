from flask import Flask, render_template, request
import random
import re
from nltk import download
from nltk.sentiment import SentimentIntensityAnalyzer
import spacy

download('vader_lexicon')  

app = Flask(__name__)

class AlienBot:
    negative_responses = ("no", "nope", "nah", "naw", "not a chance", "sorry")
    exit_commands = ("quit", "finish", "pause", "exit", "goodbye", "bi", "later")
    random_questions = ("Why do you exist?", "What is your concept of time?", "Describe your energy sources.")

    def __init__(self):
        self.alienbabble = {'describe-planet_intent': r'.*\s*your planet.*', 'answer_why_intent': r'why\sare.*', 'about_mybot': r'.*\s*mybot'}
        self.sid = SentimentIntensityAnalyzer()
        self.previous_responses = set()
        self.nlp = spacy.load("en_core_web_sm")
        self.planet_name = "Wayward Galaxies"  
        self.welcomed = False
        self.name = None  

    def greet(self, name):
        self.name = name

    def make_exit(self, reply):
        for command in self.exit_commands:
            if reply.lower() == command:
                return True
        return False

    def chat(self, initial_reply=None):
        if not self.name and not self.welcomed:
            self.greet("Earthling")  
            self.welcomed = True

        if not initial_reply:
            initial_reply = random.choice(self.random_questions).lower()

        while not self.make_exit(initial_reply):
            response = self.match_reply(initial_reply)
            while response in self.previous_responses:
                response = self.match_reply(initial_reply)

            self.previous_responses.add(response)
            if len(self.previous_responses) > 5:
                self.previous_responses.pop()

            sentiment_analysis = self.analyze_sentiment(initial_reply)
            return response, sentiment_analysis

    def match_reply(self, reply):
        doc = self.nlp(reply)

        for key, value in self.alienbabble.items():
            intent = key
            regex_pattern = value
            found_match = re.match(regex_pattern, reply)
            polite_input = any(token.text.lower() in ["please", "thank", "sorry"] for token in doc)

            if found_match and intent == 'describe-planet_intent':
                return self.describe_planet_intent()
            elif found_match and intent == 'answer_why_intent':
                return self.answer_why_intent(polite_input)
            elif found_match and intent == 'about_mybot':
                return self.about_mybot()
        if not found_match:
            return self.no_match_intent(polite_input)

    def describe_planet_intent(self):
        responses = ["My planet is a utopia of various organisms and species.",
                     f"I am from {self.planet_name}, the capital of Wayward Galaxies."]
        return random.choice(responses)

    def answer_why_intent(self, polite_input):
        if polite_input:
            responses = ["I am here in peace, embracing the harmonic connection of our cosmic existence.",
                         "Your politeness resonates across the galaxies. I am here to understand and coexist.",
                         "I appreciate your query. Exploring Earth is a manifestation of interstellar curiosity."]
        else:
            responses = ["I am an emissary of peace.",
                         "My purpose is to observe and learn about your world.",
                         "I find the enigma of Earth intriguing."]
        return random.choice(responses)

    def about_mybot(self):
        responses = ["Xylophorian Science and Knowledge Nexus welcomes you to explore the cosmos.",
                     "In the interstellar archives, mybot is renowned for disseminating wisdom across galaxies."]
        return random.choice(responses)

    def no_match_intent(self, polite_input):
        if polite_input:
            responses = ["Your insights are valued. Share more about Earth's peculiarities.",
                         "Intriguing. Please delve deeper into your earthly experiences.",
                         "Your thoughts echo across the cosmic tapestry. Elaborate further!"]
        else:
            responses = ["Fascinating. Tell me more.",
                         "Your perspective is unique. Expand upon your observations.",
                         "Curious. Why do you say that?",
                         "The enigma deepens. Can you elaborate?"]
        return random.choice(responses)

    def analyze_sentiment(self, text):
        sentiment_score = self.sid.polarity_scores(text)['compound']
        if sentiment_score >= 0.05:
            return "Your words resonate with positivity across the cosmic expanse."
        elif sentiment_score <= -0.05:
            return "I sense a wave of negativity. Let the galactic energy bring balance to your emotions."
        else:
            return "Your expressions seem neutral. The cosmic equilibrium prevails."

AlienBot = AlienBot()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def chat():
    user_input = request.form['user_input']
    response, sentiment_analysis = AlienBot.chat(user_input)
    return render_template('index.html', user_input=user_input, response=response, sentiment_analysis=sentiment_analysis)

if __name__ == '__main__':
    app.run(debug=True)

