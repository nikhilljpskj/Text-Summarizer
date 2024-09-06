# # /////////////////////////////////////////////////////////////////////////////////////////
import os
from urllib.parse import unquote
from flask import Flask, render_template, request
import youtube_transcript_api
from youtube_transcript_download    import get_video_id, download_transcript
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from bs4 import BeautifulSoup
import requests
import subprocess
import librosa
import soundfile as sf
from transformers import pipeline
import PyPDF2
from werkzeug.utils import secure_filename
import spacy

import urllib.parse
import traceback
nlp = spacy.load("en_core_web_sm")

from flask import Flask, render_template, request
from utils import read_file, get_table_data


ALLOWED_EXTENSIONS = {'txt', 'pdf'}

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__, template_folder="templates")


# Function to insert text into test.txt
from urllib.parse import unquote    
def insert_text_to_test_file(text_data):
    try:
        decoded_text = unquote(text_data)
        decoded_text = decoded_text.replace("+", " ")
        with open('filecontent.txt', 'w') as test_file:
            test_file.write(decoded_text)
        return True
    except Exception as e:
        print(f"Error inserting text into text file: {str(e)}")
        return False
    
def extract_entities(text):
    doc = nlp(text)
    entities = [ent.text for ent in doc.ents if ent.label_ in ["PERSON", "ORG", "GPE"]]
    return entities
    
# function for web scraping
def scrape_text_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            paragraphs = soup.find_all('p')
            page_text = ' '.join([paragraph.get_text() for paragraph in paragraphs])
            return page_text.strip()
        else:
            return f"Failed to retrieve data from URL: {url}. Status code: {response.status_code}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

# WSGI application to handle web requests
def application(environ, start_response):
    """Handles web requests."""
    if environ['REQUEST_METHOD'] == 'POST':
        if environ['PATH_INFO'] == '/insert':
            try:
                content_length = int(environ.get('CONTENT_LENGTH', 0))
                text_data = environ['wsgi.input'].read(content_length).decode('utf-8')
                
                if insert_text_to_test_file(text_data):
                    start_response('200 OK', [('Content-Type', 'text/plain')])
                    return ["Text inserted into test.txt successfully.".encode('utf-8')]
                else:
                    raise ValueError("Failed to insert text into test.txt.")
            except Exception as e:
                print(e)
                start_response('500 Internal Server Error', [])
                return [f"Error: {str(e)}".encode('utf-8')]
        else:
            try:
                # Get uploaded file
                uploaded_file = request.files['user_file']
                if uploaded_file.filename != '':
                    file_content = uploaded_file.read().decode('utf-8')
                    return [file_content.encode('utf-8')]
                else:
                    return ["Error: No file selected.".encode('utf-8')]
            except Exception as e:
                print(e)
                start_response('500 Internal Server Error', [])
                return [f"Error: {str(e)}".encode('utf-8')]
            
    else:
        start_response('200 OK', [('Content-Type', 'text/html')])
        open_file = open('fileupload.html', 'r')
        return [open_file.read().encode('utf-8')]

@app.route('/')
def login():
    return render_template('homepage.html')

# @app.route('/homepage', methods=['POST', 'GET'])
# def home():
#     return render_template('homepage.html')

@app.route('/aboutus', methods=['POST', 'GET'])
def aboutus():
    return render_template('aboutus.html')

@app.route('/options', methods=['POST', 'GET'])
def options():
    return render_template('options.html')


@app.route('/youtube', methods=['POST', 'GET'])
def youtube():
    return render_template('youtubesummary.html')

@app.route('/index',  methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/fileupload', methods=['GET', 'POST'])
def fileupload():
    return render_template('fileupload.html')

# 

import re
@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        try:
            # Get the uploaded file from the request
            uploaded_file = request.files['user_file']

            # Check if a file is uploaded and has an allowed extension
            if uploaded_file and allowed_file(uploaded_file.filename):
                filename = secure_filename(uploaded_file.filename)
                file_extension = filename.rsplit('.', 1)[1].lower()

                file_content = ""

                # If the file is a text file, read it directly
                if file_extension == 'txt':
                    file_content = uploaded_file.read().decode('utf-8')

                # If the file is a PDF, use PdfReader to extract the text
                elif file_extension == 'pdf':
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    for page in pdf_reader.pages:
                        # Defaulting to empty string to avoid uninitialized variable error
                        page_text = page.extract_text() or ""  # Assign default empty string if extraction fails
                        # Normalize by removing extra newlines and excessive spaces
                        normalized_text = re.sub(r'\s+', ' ', page_text).strip()
                        file_content += normalized_text + " "  # Ensure content is separated by spaces
                # Insert the text content into the test file or do something with it
                insert_text_to_test_file(file_content.strip())

                # Return the content of the uploaded file
                return file_content.strip() 
            else:
                return "Error: Invalid file or no file selected."
        except Exception as e:
            print(e)
            return f"Error: {str(e)}"
    else:
        # If the request method is not POST, return an appropriate message
        return "Method not allowed", 405
    
@app.route('/insert', methods=['POST'])
def insert():
    try:
        content_length = int(request.headers['Content-Length'])
        text_data = request.stream.read(content_length).decode('utf-8')
        
        if insert_text_to_test_file(text_data):
            return "Text inserted into test.txt successfully."
        else:
            raise ValueError("Failed to insert text into test.txt.")
    except Exception as e:
        print(e)
        return f"Error: {str(e)}", 500

# ///mAIN CHAGE



@app.route('/summarize', methods=['POST'])
def summarize():
    from summarize import clean_text, cnt_in_sent, freq_dict, calc_TF, calc_IDF, calc_TFIDF, sent_scores, summary

    input_text = request.form['text']
    def conditionally_normalize(input_text):
        # Check if there are two consecutive newline characters
            if '\n\n' in input_text:
            # Normalize text by removing paragraph breaks and extra spaces
                normalized_text = input_text.replace('\n', ' ').replace('\r', ' ')
                normalized_text = ' '.join(normalized_text.split())
            else:
            # No normalization required
                normalized_text = input_text

            return normalized_text

    normalized_text = conditionally_normalize(input_text)

    with open('test.txt', 'w') as f:
        # f.write(cleaned_text)
        f.write(normalized_text)

    with open('test.txt', 'r') as f:
        file_content = f.read()

    if not file_content.strip():
        return "File is empty or does not contain any data. No data to summarize."
    
    # Generate summary
    sentences = clean_text('test.txt')
    # if not sentences:
    #     return "File is empty or does not contain any data. No data to summarize."
    text_data = cnt_in_sent(sentences)
    freq_list = freq_dict(sentences)
    tf_scores = calc_TF(text_data, freq_list)
    idf_scores = calc_IDF(text_data, freq_list)
    tfidf_scores = calc_TFIDF(tf_scores, idf_scores)
    sent_data = sent_scores(tfidf_scores, sentences, text_data)
    result = summary(sent_data)

    return render_template('index.html', input_text=input_text, summary=result)

# /////

@app.route('/summarizeurl', methods=['POST'])
def summarizeurl():
    from summarizeurl import clean_texturl, cnt_in_senturl, freq_dicturl, calc_TFurl, calc_IDFurl, calc_TFIDFurl, sent_scoresurl, summaryurl

    input_text = request.form['text']

    if not input_text:
            return "Error: No input text provided.", 

        # Remove square brackets, dollar signs, and digits from the text
    cleaned_text = re.sub(r'[\[\]\$\d\-\*\+\!\)\(\%]', '', input_text)

        # Write the cleaned text to 'url.txt'
    with open('url.txt', 'w', encoding='utf-8') as f:
            f.write(cleaned_text)

    # with open('url.txt', 'w') as f:
    #     f.write(input_text)

    sentences = clean_texturl('url.txt')
    text_data = cnt_in_senturl(sentences)
    freq_list = freq_dicturl(sentences)
    tf_scores = calc_TFurl(text_data, freq_list)
    idf_scores = calc_IDFurl(text_data, freq_list)
    tfidf_scores = calc_TFIDFurl(tf_scores, idf_scores)
    sent_data = sent_scoresurl(tfidf_scores, sentences, text_data)
    result = summaryurl(sent_data)

    return render_template('urlsummary.html', input_text=input_text, summary=result)


from flask import request, render_template

@app.route('/summarizefile', methods=['POST'])
def summarizefile():
    from summarizefile import clean_textfile, cnt_in_sentfile, freq_dictfile, calc_TFfile, calc_IDFfile, calc_TFIDFfile, sent_scoresfile, summaryfile
    try:
        input_text = request.form['text']

        # Insert text into the test file
        if not insert_text_to_test_file(input_text):
            return "Error inserting text into the test file."

        # Clean text and generate summary
        sentences = clean_textfile('filecontent.txt')
        text_data = cnt_in_sentfile(sentences)
        freq_list = freq_dictfile(sentences)
        tf_scores = calc_TFfile(text_data, freq_list)
        idf_scores = calc_IDFfile(text_data, freq_list)
        tfidf_scores = calc_TFIDFfile(tf_scores, idf_scores)
        sent_data = sent_scoresfile(tfidf_scores, sentences, text_data)
        result = summaryfile(sent_data)
        # print("result is:"+ result)
        # print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        return result
        # Return the summary to the client
        # return render_template('fileupload.html', summaryResult=result)

    except Exception as e:
        print(f"Error summarizing file: {str(e)}")
        # return "Error summarizing file."

    

# summarizer = pipeline('summarization', model='sreyassc/text_summary')

@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    from summarizer import summarize_text
    youtube_link = request.form['youtube_link']
    unique_id = get_video_id(youtube_link)

    if unique_id:
        try:
            transcript_text = download_transcript(unique_id)
            transcript_text = ' '.join(transcript_text.split())
            transcript_text = transcript_text.replace('\n', ' ')
            
            if transcript_text:
                # Summarize the transcript text
                summary_text = summarize_text(transcript_text)
                print("Generated summary:", summary_text)
                return render_template('youtubesummary.html', transcript=transcript_text, summary=summary_text)
            else:
                error_message = "Error fetching transcript. Please try again later."
                return render_template('youtubesummary.html', error_message=error_message)
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            return render_template('youtubesummary.html', error_message=error_message)
    else:
        error_message = "Invalid YouTube URL."
        return render_template('youtubesummary.html', error_message=error_message)
    

from flask import Flask, render_template, request
from summarizer import summarize_text

@app.route('/get_transcript_summary', methods=['POST'])
def get_transcript_summary():
    print("Request received for transcript summary...")
    print("Form data:", request.form)
    transcript_text = request.form['transcript_input']
    print(transcript_text)
    print("Transcript text:", transcript_text)
    print("Length of transcript text:", len(transcript_text.split()))

    # Summarize the transcript text
    summary_text = summarize_text(transcript_text)
    # print("Generated summary:", summary_text)

    return render_template('youtubesummary.html', transcript=transcript_text, summary=summary_text)


@app.route('/urlsummarize')
def urlsummarize():
    return render_template('urlsummary.html')

@app.route('/extract_text_url', methods=['POST'])
def extract_text():
    url = request.form['url']
    text_data = scrape_text_from_url(url)
    return render_template('urlsummary.html', url=url, extracted_text=text_data)


if __name__ == '__main__':
    app.run(debug=True)
