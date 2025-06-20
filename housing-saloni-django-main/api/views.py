from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ScrappedData, OpenAIAnalysis, NewOpenAIAnalysis
import pandas as pd
import io
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login 
from .utils import get_user_from_token
from rest_framework.authtoken.models import Token


def index(request):
    return JsonResponse({'message': 'Hello, world!'})

@csrf_exempt
def upload_file_view(request):
    if request.method == 'POST':
        print('POST request received')
        uploaded_file = request.FILES.get('file')
        
        if uploaded_file:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            # Ensure the uploaded file is a supported format
            if file_extension in ['csv', 'xlsx', 'xls', 'xlsm']:
                try:
                    # Read file into a DataFrame
                    if file_extension == 'csv':
                        df = pd.read_csv(io.StringIO(uploaded_file.read().decode('utf-8')))
                    else:
                        df = pd.read_excel(uploaded_file)
                    
                    # Check if required columns exist
                    if 'URL' in df.columns and 'Description' in df.columns:
                        for _, row in df.iterrows():
                            ScrappedData.objects.create(
                                url=row['URL'],
                                description=row['Description']
                            )
                        messages.success(request, 'Data uploaded successfully!')
                    else:
                        messages.error(request, 'The file must contain "URL" and "Description" columns.')
                except Exception as e:
                    messages.error(request, f"Error processing file: {e}")
            else:
                messages.error(request, "Unsupported file format. Please upload a CSV or Excel file.")
        return redirect('upload_file_view')
    return render(request, 'upload.html')

@csrf_exempt
def delete_scrapped_data(request, pk):
    scrapped_data = ScrappedData.objects.get(pk=pk)
    scrapped_data.deleted = True
    scrapped_data.save()
    return JsonResponse({'message': 'Data deleted successfully!'}, status=200)

@csrf_exempt
def mark_issue(request, pk):
    scrapped_data = ScrappedData.objects.get(pk=pk)
    scrapped_data.issue = True
    scrapped_data.save()
    return JsonResponse({'message': 'Data marked as issue!'}, status=200)

@csrf_exempt
def analysis(request):
    if request.method == 'POST':
        # Get the raw body of the POST request and parse it into a dictionary
        body = json.loads(request.body)

        # Extract the fields from the parsed JSON
        url = body.get('url')
        description = body.get('description')
        summary_data = body.get('summary')

        print(url, description, summary_data)

        # Create an instance of OpenAIAnalysis and save it to the database
        analysis_entry = OpenAIAnalysis(
            url=url,
            description=description,
            religion=summary_data.get('religion', ''),
            race_color_national_origin=summary_data.get('race_color_national_origin', ''),
            sex_gender_preferences=summary_data.get('sex_gender_preferences', ''),
            disability=summary_data.get('disability', ''),
            familial_status=summary_data.get('familial_status', ''),
            source_of_income=summary_data.get('source_of_income', ''),
            arrest_conviction_records=summary_data.get('arrest_conviction_records', ''),
            eviction_history=summary_data.get('eviction_history', ''),
            credit_score_employment=summary_data.get('credit_score_employment', ''),
            coded_language=summary_data.get('coded_language', ''),
            discriminatory=summary_data.get('discriminatory', '')
        )
        analysis_entry.save()

        # Return a success response
        return JsonResponse({"message": "Analysis saved successfully."}, status=200)

    # elif request.method == 'GET':
    #     # Get all analysis entries from the database
    #     analysis_entries = OpenAIAnalysis.objects.all()

    #     # Create a list of dictionaries to store the data
    #     analysis_data = []
    #     for entry in analysis_entries:
    #         data = {
    #             "url": entry.url,
    #             "description": entry.description,
    #             "religion": entry.religion,
    #             "race_color_national_origin": entry.race_color_national_origin,
    #             "sex_gender_preferences": entry.sex_gender_preferences,
    #             "disability": entry.disability,
    #             "familial_status": entry.familial_status,
    #             "source_of_income": entry.source_of_income,
    #             "arrest_conviction_records": entry.arrest_conviction_records,
    #             "eviction_history": entry.eviction_history,
    #             "credit_score_employment": entry.credit_score_employment,
    #             "coded_language": entry.coded_language,
    #         }
    #         analysis_data.append(data)

    #     # Return the data as a JSON response
    #     return JsonResponse(analysis_data, safe=False)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@csrf_exempt
def get_analysis(request, page_number=1):
    if request.method == 'GET':
        # Get all analysis entries from the database
        analysis_entries = OpenAIAnalysis.objects.all().order_by('id')

        # Create a Paginator object to paginate results
        paginator = Paginator(analysis_entries, 50)  # 100 items per page
        try:
            page = paginator.page(page_number)
        except EmptyPage:
            return JsonResponse({"error": "Page not found."}, status=404)

        # Create a list of dictionaries to store the data
        analysis_data = []
        for entry in page:
            data = {
                "id": entry.id,
                "url": entry.url,
                "description": entry.description,
                "religion": entry.religion,
                "race_color_national_origin": entry.race_color_national_origin,
                "sex_gender_preferences": entry.sex_gender_preferences,
                "disability": entry.disability,
                "familial_status": entry.familial_status,
                "source_of_income": entry.source_of_income,
                "arrest_conviction_records": entry.arrest_conviction_records,
                "eviction_history": entry.eviction_history,
                "credit_score_employment": entry.credit_score_employment,
                "coded_language": entry.coded_language,
                "discriminatory": entry.discriminatory,
            }
            analysis_data.append(data)

        # Return the data as a JSON response
        return JsonResponse(analysis_data, safe=False)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@csrf_exempt
def new_analysis(request):
    if request.method == 'POST':
        try:
            # Parse incoming JSON data
            body = json.loads(request.body)

            # Extract main fields
            url = body.get('url')
            main_description = body.get('main_description')
            analysis_data = body.get('summary', {})

            # Extract analysis details
            comments = analysis_data.get('comments', [])  # List of comments
            categories = analysis_data.get('categories', [])  # List of categories
            flagged = analysis_data.get('flagged', "false")  # Boolean flag
            analysis = json.dumps(analysis_data)  # Store the entire analysis JSON as text

            # Create an instance and save to the database
            analysis_entry = NewOpenAIAnalysis(
                url=url,
                description=main_description,
                analysis=analysis,
                comments=comments,  # JSON field
                categories=categories,  # JSON field
                isDiscriminatory=flagged
            )
            analysis_entry.save()

            return JsonResponse({"message": "Analysis saved successfully."}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    # elif request.method == 'GET':
    #     # Get all stored analysis entries
    #     analysis_entries = NewOpenAIAnalysis.objects.all().values(
    #         "url", "description", "comments", "categories", "flagged"
    #     )

    #     return JsonResponse(list(analysis_entries), safe=False)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@csrf_exempt
def get_new_analysis(request, page_number=1):
    user = get_user_from_token(request)
    if not user:
        return JsonResponse({"error": "Unauthorized."}, status=401)
    if request.method == 'GET':
        try:
            # Get all analysis entries ordered by ID
            analysis_entries = NewOpenAIAnalysis.objects.all().order_by('id')

            # Filter entries where the 'analysis' JSON contains 'is_discriminatory': True
            filtered_entries = NewOpenAIAnalysis.objects.none()  # Start with an empty QuerySet
            for entry in analysis_entries:
                try:
                    # Parse the JSON in the 'analysis' field
                    analysis_data = json.loads(entry.analysis)
                    # If 'is_discriminatory' is True, include the entry
                    if analysis_data.get('is_discriminatory', False):
                        filtered_entries |= NewOpenAIAnalysis.objects.filter(id=entry.id)  # Combine into QuerySet
                except json.JSONDecodeError:
                    continue  # Skip entries where the analysis field is not valid JSON

            # Paginate the filtered QuerySet (50 entries per page)
            paginator = Paginator(filtered_entries, 50)

            # Get requested page
            page = paginator.page(page_number)

            # Serialize data for the response
            analysis_data = list(page.object_list.values(
                "id", "url", "description", "comments", "analysis", "flagged"
            ))

            # Return paginated results along with pagination info
            return JsonResponse({
                "page": page_number,
                "total_pages": paginator.num_pages,
                "total_entries": paginator.count,
                "data": analysis_data
            }, safe=False)

        except EmptyPage:
            return JsonResponse({"error": "Page not found."}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@csrf_exempt
def add_tag(request, pk):
    if request.method == 'POST':
        # Get the raw body of the POST request and parse it into a dictionary
        body = json.loads(request.body)

        # Extract the tag from the parsed JSON
        tag = body.get('tag')

        # Get the analysis entry
        analysis_entry = NewOpenAIAnalysis.objects.get(pk=pk)

        analysis_entry.comments.append(tag)  # Assuming comments is a list field
        analysis_entry.save()

        return JsonResponse({"message": "Tag added successfully."}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@csrf_exempt
def search_tag(request):
    # Get based search query from request
    if request.method == 'GET':
        query = request.GET.get('query', '').strip()
        if not query:
            return JsonResponse({"error": "No search query provided."}, status=400)

        # Search for analysis entries that contain the query in their comments
        analysis_entries = NewOpenAIAnalysis.objects.filter(comments__icontains=query)

        # Serialize data for the response
        analysis_data = list(analysis_entries.values(
            "id", "url", "description", "comments", "analysis", "flagged"
        ))

        return JsonResponse(analysis_data, safe=False)
    
    return JsonResponse({"error": "Invalid request method."}, status=405)

@csrf_exempt
def delete_tag(request, pk):
    if request.method == 'POST':
        try:
            # Parse the request body
            body = json.loads(request.body)
            tag = body.get('tag')

            if not tag:
                return JsonResponse({"error": "Tag not provided."}, status=400)

            # Fetch the analysis entry
            analysis_entry = NewOpenAIAnalysis.objects.get(pk=pk)
            print(f"Deleting tag: {tag} from analysis entry with ID: {analysis_entry.comments}")

            # Ensure comments is a list of lists
            if isinstance(analysis_entry.comments, list):
                # Check if the tag exists in any of the nested lists
                for sublist in analysis_entry.comments:
                    print(f"Checking sublist: {sublist} for tag: {tag}")
                    if tag in sublist:
                        sublist.remove(tag)  # Remove the tag
                        analysis_entry.save()
                        return JsonResponse({"message": "Tag deleted successfully."}, status=200)

                return JsonResponse({"error": "Tag not found."}, status=404)
            else:
                return JsonResponse({"error": "Comments field is not a list of lists."}, status=400)

        except NewOpenAIAnalysis.DoesNotExist:
            return JsonResponse({"error": "Analysis entry not found."}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@csrf_exempt
def human_feedback(request, pk):
    if request.method == 'POST':
        # Get the analysis entry
        analysis_entry = NewOpenAIAnalysis.objects.get(pk=pk)

        if analysis_entry.flagged:
            analysis_entry.flagged = False
        else: 
            analysis_entry.flagged = True
            
        analysis_entry.save()

        return JsonResponse({"message": "Feedback saved successfully."}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)
    

@csrf_exempt
def sign_up(request):
    if request.method == 'POST':
        # Get the raw body of the POST request and parse it into a dictionary
        body = json.loads(request.body)

        # Extract the fields from the parsed JSON
        first_name = body.get('first_name')
        last_name = body.get('last_name')
        email = body.get('email')
        username = email
        password = body.get('password')

        # email should end with @open-communities.org
        if not email.endswith('@open-communities.org'):
            return JsonResponse({"error": "Invalid email address."}, status=400)

        # Check if the username is already taken
        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already taken."}, status=400)

        # Create a new user and save it to the database
        user = User.objects.create_user(username=username, password=password, email=email)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Return a success response
        return JsonResponse({"message": "User created successfully."}, status=201)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@csrf_exempt
def login(request):
    if request.method == 'POST':
        # Get the raw body of the POST request and parse it into a dictionary
        body = json.loads(request.body)

        # Extract the fields from the parsed JSON
        username = body.get('email')
        password = body.get('password')

        # Ensure email ends with @open-communities.org
        if not username.endswith('@open-communities.org'):
            return JsonResponse({"error": "Invalid email address."}, status=400)

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        # Check if the user is authenticated
        if user is not None:
            auth_login(request, user)
            # Get or create the token for the authenticated user
            token, created = Token.objects.get_or_create(user=user)
            return JsonResponse({"message": "User authenticated successfully.", "token": token.key}, status=200)
        else:
            return JsonResponse({"error": "Invalid credentials."}, status=401)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@csrf_exempt
def logout(request):
    if request.method == 'POST':
        # Log the user out
        logout(request)
        return JsonResponse({"message": "User logged out successfully."}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)