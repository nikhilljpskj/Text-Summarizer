# from django.shortcuts import render
# from django.http import HttpResponse
# from .utils import read_file, get_table_data
# from .mcqgenerator import generate_evaluate_chain
# import json

# # Load RESPONSE_JSON from a JSON file
# with open("D:\cognitize\cognitize\Response.json", 'r') as file:
#     RESPONSE_JSON = json.load(file)


# def mcq_generator_view(request):
#     if request.method == 'POST':
#         uploaded_file = request.FILES.get('file')
#         mcq_count = int(request.POST.get('mcq_count'))
#         subject = request.POST.get('subject')
#         tone = request.POST.get('tone')

#         try:
#             text = read_file(uploaded_file)
#             response = generate_evaluate_chain(
#                 {
#                     "text": text,
#                     "number": mcq_count,
#                     "subject": subject,
#                     "tone": tone,
#                     "RESPONSE_JSON": json.dumps(RESPONSE_JSON)
#                 }
#             )

#             if isinstance(response, dict):
#                 quiz = response.get("quiz", None)
#                 if quiz is not None:
#                     table_data = get_table_data(quiz)
#                     if table_data is not None:
#                         return render(request, 'result2.html',
#                                       {'table_data': table_data, 'review': response['review']})
#                     else:
#                         return HttpResponse("Error in table data")
#                 else:
#                     return HttpResponse("Error in quiz generation")
#             else:
#                 return HttpResponse(str(response))

#         except Exception as e:
#             return HttpResponse(str(e))

#     return render(request, 'home2.html')

