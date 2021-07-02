# Meet Robo: your friend

# import necessary libraries

import random #random number generator
import string  # to process standard python strings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings #warning genarate for errors
import playsound #voice recognition and genarate sound
import speech_recognition as sr #voice recognition
from datetime import datetime#use to get current date and time
from gtts import gTTS #google voice
import os #Operating system process control
import tempfile# printing
import win32api#printing
import win32print#printiing
from pathlib import Path #printing document
printer_name = win32print.GetDefaultPrinter ()#connect to system default printer

warnings.filterwarnings('ignore')

import nltk
from nltk.stem import WordNetLemmatizer

nltk.download('popular', quiet=True)  # for downloading packages

# uncomment the following only the first time
# nltk.download('punkt') # first-time use only
# nltk.download('wordnet') # first-time use only


# Reading in the corpus
with open('chatbot.txt', 'r', encoding='utf8', errors='ignore') as fin:
    raw = fin.read().lower()

# TOkenisation
sent_tokens = nltk.sent_tokenize(raw)  # converts to list of sentences
word_tokens = nltk.word_tokenize(raw)  # converts to list of words

# Preprocessing
lemmer = WordNetLemmatizer()


def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]


remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)


def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))


# Keyword Matching
GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up", "hey",)
GREETING_RESPONSES = ["hi, how can I help you?", "Hey :-)", "Hello do need a help to find a good", "thanks for visiting our supper market , how can i help you?", "Hi there, what can I do for you?", "hello, how can I help you?", "I am glad! You are talking to me"]


def greeting(sentence):
    """If user's input is a greeting, return a greeting response"""
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)


# Generating response
def response(user_response):
    robo_response = ''
    sent_tokens.append(user_response)
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx = vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    if (req_tfidf < 0):
        robo_response = robo_response + " do you need another help?"
        return robo_response
    if (req_tfidf == 0):
        robo_response = robo_response + "please try again"
        user_response=''
        return robo_response
    else:
        robo_response = robo_response + sent_tokens[idx]
        return robo_response


# speech recognition
def alexis_speak(audio_string):
    tts = gTTS(text=audio_string, lang='en')
    print("Alexa :" + audio_string)
    #write_to_file(now.strftime("%d%m%y %H:%M:%S") + audio_string)
    r = random.randint(1, 10000000)
    audio_file = 'audio-' + str(r) + '.mp3'
    tts.save(audio_file)
    playsound.playsound(audio_file)
    os.remove(audio_file)


# write the chat in a text file
def write_to_file(find_result):
    text_file = open("sample.txt", "a")
    n = text_file.write(find_result + "\n")
    text_file.close()


# get the user voice and record to a mp3 audio clip and some covetting to string quotes
def record_audio():
    r = sr.Recognizer()
    with sr.Microphone()as source:
        audio = r.listen(source)
    user_response =''
    try:
        print("You:" + r.recognize_google(audio))
        user_response = r.recognize_google(audio)
        user_response = user_response.lower()

    except sr.UnknownValueError:
        alexis_speak("Google speech recognition could not understand your audio..")
        user_response = ''
    except sr.RequestError:
        alexis_speak("sorry ,my speech service is down..")
    return user_response


# datetime object containing current date and time
now = datetime.now()

flag = True
alexis_speak("I am Alexa. I can help you to find items in supermarket.")
alexis_speak("say something to me")
while (flag == True):
    user_response = record_audio()
    if (user_response != 'bye'):
        if (user_response == 'thanks' or user_response == 'thank you' or user_response == 'no'):
            flag = False
            alexis_speak("Thank for using  Alexa supermarket chatBot service! you are welcome again..")
            os.remove("sample.txt")
            break
        if (greeting(user_response) != None):
            alexis_speak(greeting(user_response))


        else:
            if (user_response == 'print'):
                flag = True
                countriesStr = Path('sample.txt').read_text()
                filename = tempfile.mktemp(".txt")
                open(filename, "w").write(countriesStr)

                alexis_speak(
                    "your important most parts of your current chat history is send to the printer to print now, do you need more help.")

                win32api.ShellExecute(
                    0,
                    "print",
                    filename,
                    #
                    # If this is None, the default printer will
                    # be used anyway.
                    #
                    '/d:"%s"' % win32print.GetDefaultPrinter(),
                    ".",
                    0
                )

                alexis_speak("Do you need more service!")

            else:
                # print("Alexa: ", end="")
                str123 = response(user_response)
                alexis_speak(str123)

                if(str123 != 'please try again' ):
                    write_to_file(now.strftime("%d%m%y %H:%M:%S") + str123)

                sent_tokens.remove(user_response)


    if (user_response == 'exit'):
        flag = False
        os.remove("sample.txt")
        alexis_speak("Bye! you are welcome again..")

