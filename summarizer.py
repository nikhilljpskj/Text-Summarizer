# # # from transformers import pipeline
# # # summarizer = pipeline('summarization',model='sreyassc/text_summary')
# # # # Define the summarize_text function
# # # def summarize_text(text):
# # #     summarizer = pipeline('summarization', model='sreyassc/text_summary')
# # #     summary = summarizer(text, max_length=100, min_length=10, do_sample=False)[0]['summary_text']
# # #     return summary



# # from transformers import pipeline

# # summarizer = pipeline('summarization', model='sreyassc/text_summary')

# # def summarize_text(text, max_length=100):
# #     input_length = len(text.split())
# #     if max_length > input_length:
# #         max_length = input_length - 1  # Set max_length to a value close to input_length
        
# #     # Generate the summary
# #     summary = summarizer(text, max_length=max_length, min_length=10, do_sample=False)[0]['summary_text']
# #     return summary

# from transformers import pipeline

# summarizer = pipeline('summarization', model='sreyassc/text_summary')

# def summarize_text(text, max_length=100):
#     # Determine the length of the input text
#     input_length = len(text.split())
    
#     # Check if the max_length is too small
#     if max_length < input_length:
#         max_length = input_length + 10  # Increase max_length to accommodate the input
    
#     # Generate the summary
#     summary = summarizer(text, max_length=max_length, min_length=10, do_sample=False)[0]['summary_text']
#     return summary
from transformers import pipeline

summarizer = pipeline('summarization', model='sreyassc/text_summary')
def summarize_text(text, max_length=100):
    # Determine the length of the input text
    input_length = len(text.split())
    
    # Check if the max_length is too small
    if max_length < input_length:
        max_length = input_length + 10  # Increase max_length to accommodate the input
    
    # Generate the summary
    summary = summarizer(text, max_length=max_length, min_length=10, do_sample=False)[0]['summary_text']
    return summary
