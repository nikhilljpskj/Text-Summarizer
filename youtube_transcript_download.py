from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import requests
import re
import os
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline


app = Flask(__name__)

# tokenizer = AutoTokenizer.from_pretrained("oliverguhr/fullstop-punctuation-multilang-large")
# model = AutoModelForTokenClassification.from_pretrained("oliverguhr/fullstop-punctuation-multilang-large")
# punctuation_pipeline = pipeline('ner', model=model, tokenizer=tokenizer)


def get_video_id(youtube_url):
    # Function to extract video ID from YouTube URL
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, youtube_url)
    return match.group(1) if match else None

def download_transcript(video_id):
    # Function to download transcript for the given video ID
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_generated_transcript(['en'])

        formatter = TextFormatter()
        transcript_text = formatter.format_transcript(transcript.fetch())

        # Remove timecodes and speaker names
        transcript_text = re.sub(r'\[\d+:\d+:\d+\]', '', transcript_text)
        transcript_text = re.sub(r'<\w+>', '', transcript_text)
        return transcript_text
    except Exception as e:
        print(f"Error downloading transcript: {e}")
        return ""

@app.route('/youtube')
def index():
    # Render index.html with form to input YouTube URL
    return render_template('youtubesummary.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    if request.method == 'POST':
        youtube_url = request.form['youtube_url']
        video_id = get_video_id(youtube_url)

        if video_id:
            transcript_text = download_transcript(video_id)
            if transcript_text:
                # Save transcript to test.txt
                with open('test.txt', 'w', encoding='utf-8') as file:
                    file.write(transcript_text)

                # Render transcript.html with transcript text
                return render_template('transcript.html', transcript_text=transcript_text)
            else:
                error_message = "Unable to download transcript."
                return render_template('index.html', error=error_message)
        else:
            error_message = "Invalid YouTube URL."
            return render_template('index.html', error=error_message)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
# from flask import Flask, render_template, request
# from youtube_transcript_api import YouTubeTranscriptApi
# from youtube_transcript_api.formatters import TextFormatter
# import requests
# import re
# import os
# # from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# app = Flask(__name__)

# # Load the tokenizer and model for punctuation prediction
# # tokenizer = AutoTokenizer.from_pretrained("oliverguhr/fullstop-punctuation-multilang-large")
# # model = AutoModelForTokenClassification.from_pretrained("oliverguhr/fullstop-punctuation-multilang-large")
# # punctuation_pipeline = pipeline('ner', model=model, tokenizer=tokenizer)

# def get_video_id(youtube_url):
#     # Function to extract video ID from YouTube URL
#     pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
#     match = re.search(pattern, youtube_url)
#     return match.group(1) if match else None

# def download_transcript(video_id):
#     # Function to download transcript for the given video ID
#     try:
#         transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
#         transcript = transcript_list.find_generated_transcript(['en'])

#         formatter = TextFormatter()
#         transcript_text = formatter.format_transcript(transcript.fetch())

#         # Remove timecodes and speaker names
#         transcript_text = re.sub(r'\[\d+:\d+:\d+\]', '', transcript_text)
#         transcript_text = re.sub(r'<\w+>', '', transcript_text)
#         return transcript_text
#     except Exception as e:
#         print(f"Error downloading transcript: {e}")
#         return ""

# @app.route('/')
# def index():
#     # Render index.html with form to input YouTube URL
#     return render_template('index.html')

# @app.route('/summarize', methods=['POST'])
# def summarize():
#     if request.method == 'POST':
#         youtube_url = request.form['youtube_url']
#         video_id = get_video_id(youtube_url)

#         if video_id:
#             transcript_text = download_transcript(video_id)
#             if transcript_text:
#                 # Get punctuation predictions
#                 output_json = punctuation_pipeline(transcript_text)
#                 # Construct the punctuated transcript
#                 punctuated_transcript = ''
#                 for n in output_json:
#                     word = n['word'].replace('▁', ' ')  # Replace special tokens used by tokenizer
#                     entity = n['entity'].replace('LABEL_', '')  # Strip the 'LABEL_' prefix
#                     if entity == '0':
#                         punctuated_transcript += word  # No punctuation needed
#                     else:
#                         punctuated_transcript += word + entity  # Add the predicted punctuation

#                 # Render index.html with punctuated transcript text
#                 return render_template('index.html', transcript=punctuated_transcript)
#             else:
#                 error_message = "Unable to download transcript."
#                 return render_template('index.html', error=error_message)
#         else:
#             error_message = "Invalid YouTube URL."
#             return render_template('index.html', error=error_message)
#     else:
#         return render_template('index.html')

# if __name__ == '__main__':
#     app.run(debug=True)
