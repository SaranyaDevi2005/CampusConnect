from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
import pymongo 
from django import forms
from .forms import AddCompanyForm, AddPlacementDetailsForm, AddPlacementCoordinatorForm,AddStudentForm,StudentDetailsForm
from .decorators import role_required
from django.http import JsonResponse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from collections import Counter,defaultdict

# Connect to MongoDB
client = pymongo.MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]
user_collection = db['user']  # The collection where user data is stored
students_collection = db['Student']
# Choices for the login form
ROLE_CHOICES = [
    ('Teacher', 'Teacher'),
    ('placement cordinator', 'Placement Cordinator'),
    ('student', 'Student'),
]

# Form for login
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Role')

def login_view(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password'].strip()
            role = form.cleaned_data['role'].strip()

            print(f"Attempting login with - Username: '{username}', Password: '{password}', Role: '{role}'")

            try:
                # Query MongoDB for the user with username and password
                user = user_collection.find_one({
                    'Username': {'$regex': f'^{username}$', '$options': 'i'},
                    'Password': password
                })

                print(f"User query result: {user}")

                if user:
                    # Compare the provided role with the stored role
                    stored_role = user['Role'].strip()  # Clean the stored role
                    print(f"Stored role: '{stored_role}', Provided role: '{role}'")

                    if stored_role.lower() == role.lower():  # Compare roles
                        # Set session variables
                        request.session['username'] = username
                        request.session['role'] = stored_role.lower()

                        # Redirect based on role
                        if role.lower() == 'teacher':
                            return redirect('teacher_dashboard')
                        elif role.lower() == 'placement cordinator':
                            return redirect('placement_coordinator_dashboard')
                        elif role.lower() == 'student':
                            return redirect('student_dashboard')
                        else:
                            messages.error(request, "Unknown role")
                            return redirect('login')
                    else:
                        messages.error(request, "Role mismatch")
                        return redirect('login')
                else:
                    messages.error(request, "Invalid username or password")
                    return redirect('login')

            except Exception as e:
                messages.error(request, f"Error querying database: {e}")
                return redirect('login')

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    try:
        del request.session['username']
        del request.session['role']
    except KeyError:
        pass
    messages.success(request, "You have been logged out.")
    return redirect('login')

@role_required(allowed_roles=['teacher', 'placement cordinator'])
def add_company_view(request):
    if request.method == 'POST':
        form = AddCompanyForm(request.POST)
        if form.is_valid():
            company_name = form.cleaned_data['company_name']
            dream_non_dream = form.cleaned_data['dream_non_dream']
            offer_type = form.cleaned_data['offer_type']
            role = form.cleaned_data['role']

            # Save company details to the 'company' collection in MongoDB
            try:
                company_collection = db['Company']  # Change to your company collection name
                company_collection.insert_one({
                    'Company Name': company_name,
                    'DREAM/NON-DREAM': dream_non_dream,
                    'OFFER FOR': offer_type,
                    'Role': role
                })
                
                # Redirect based on user role
                if request.session['role'] == 'teacher':
                    return redirect('teacher_dashboard')
                else:
                    return redirect('placement_coordinator_dashboard')
            except Exception as e:
                messages.error(request, f"Error saving company: {e}")
    else:
        form = AddCompanyForm()
    return render(request, 'accounts/add_company.html', {'form': form})


@role_required(allowed_roles=['teacher', 'placement cordinator'])
def add_placement_details_view(request):
    user_role = request.session.get('role')  # Retrieve the user's role from the session

    # Fetch company names from MongoDB
    company_collection = db['Company']
    companies = company_collection.find({}, {"_id": 0, "Company Name": 1})  # Get only company names

    company_choices = [(company['Company Name'], company['Company Name']) for company in companies]

    if request.method == 'POST':
        form = AddPlacementDetailsForm(request.POST)
        form.fields['company_name'].choices = company_choices  # Set the choices dynamically

        if form.is_valid():
            company_name = form.cleaned_data['company_name']
            students_1st_round = form.cleaned_data['students_1st_round']
            students_2nd_round = form.cleaned_data['students_2nd_round']
            students_final_round = form.cleaned_data['students_final_round']
            students_final_names = form.cleaned_data['students_final_names']
            students_selected = form.cleaned_data['students_selected']
            students_selected_names = form.cleaned_data['students_selected_names']

            # Save placement details to the 'placement' collection in MongoDB
            try:
                placement_collection = db['placement']  # Use your 'placement' collection
                placement_collection.insert_one({
                    'Company Name': company_name,
                    'Students 1st Round': students_1st_round,
                    'Students 2nd Round': students_2nd_round,
                    'Students Final Round': students_final_round,
                    'Students Final Names': [name.strip() for name in students_final_names.split(',')],
                    'Students Selected': students_selected,
                    'Students Selected Names': [name.strip() for name in students_selected_names.split(',')]
                })
                messages.success(request, "Placement details added successfully! You can add more details below.")

                # Clear the form by instantiating a new one
                form = AddPlacementDetailsForm()
                form.fields['company_name'].choices = company_choices  # Re-populate choices
            except Exception as e:
                messages.error(request, f"Error saving placement details: {e}")
    else:
        form = AddPlacementDetailsForm()
        form.fields['company_name'].choices = company_choices  # Populate choices on GET request

    context = {
        'form': form,
        'user_role': user_role  # Pass the user's role to the template
    }

    return render(request, 'accounts/add_placement_details.html', context)

@role_required(allowed_roles=['teacher'])
def add_placement_coordinator_view(request):
    if request.method == 'POST':
        form = AddPlacementCoordinatorForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            role = 'Placement Coordinator'  # Default role

            # Save placement coordinator details to MongoDB
            try:
                existing_user = user_collection.find_one({'Username': username})
                if existing_user:
                    messages.error(request, "Username already exists.")
                else:
                    user_collection.insert_one({
                        'Username': username,
                        'Password': password,
                        'Role': role
                    })
                    
                    # Render the form again with a success message
                    return render(request, 'accounts/add_placement_coordinator.html', {
                        'form': AddPlacementCoordinatorForm(),  # Reset the form
                        'success_message': "Placement Coordinator added successfully! You can add another."
                    })
            except Exception as e:
                messages.error(request, f"Error adding placement coordinator: {e}")
    else:
        form = AddPlacementCoordinatorForm()
    
    return render(request, 'accounts/add_placement_coordinator.html', {'form': form})


@role_required(allowed_roles=['placement cordinator'])
def add_students_view(request):
    if request.method == 'POST':
        form = AddStudentForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            role = 'Student'  # Default role

            # Save placement coordinator details to MongoDB
            try:
                existing_user = user_collection.find_one({'Username': username})
                if existing_user:
                    messages.error(request, "Username already exists.")
                else:
                    user_collection.insert_one({
                        'Username': username,
                        'Password': password,
                        'Role': role
                    })
                    
                    # Render the form again with a success message
                    return render(request, 'accounts/add_students.html', {
                        'form': AddStudentForm(),  # Reset the form
                        'success_message': "Student added successfully! You can add another."
                    })
            except Exception as e:
                messages.error(request, f"Error adding Student: {e}")
    else:
        form = AddPlacementCoordinatorForm()
    
    return render(request, 'accounts/add_students.html', {'form': form})



from collections import Counter

def view_details_view(request):
    try:
        # Retrieve all companies from the placement collection
        placement_collection = db['placement']
        company_collection = db['Company']

        # Find all placements
        placements = list(placement_collection.find({}))
        

        # Get a set of unique company names from placements
        placement_company_names = {placement['Company Name'] for placement in placements}
       
        # Retrieve corresponding rows from the Company collection
        companies = list(company_collection.find({'Company Name': {'$in': list(placement_company_names)}}))
        

        # Prepare data for graphs
        total_companies = len(companies)
        
        # Number of companies in dream/non-dream category
        dream_non_dream_count = Counter(company.get('DREAM/NON-DREAM', 'Unknown') for company in companies)

        # Number of companies for MSC, Both, and Engineering
        offer_type_count = Counter(company.get('OFFER FOR', 'Unknown') for company in companies)

        # Initialize counts for roles
        role_counts = {
            'Software Related': {'company_count': 0, 'company_names': [], 'original_roles': []},
            'AI Related': {'company_count': 0, 'company_names': [], 'original_roles': []},
            'Data Science': {'company_count': 0, 'company_names': [], 'original_roles': []},
            'Others': {'company_count': 0, 'company_names': [], 'original_roles': []}
        }

        for company in companies:
            role = company.get(' Role', 'Unknown').strip()  # Make sure to remove leading/trailing spaces
            company_name = company.get('Company Name', 'Unknown Company')

            # Classify roles based on keywords
            if 'Software' in role:
                role_counts['Software Related']['company_count'] += 1
                role_counts['Software Related']['company_names'].append(company_name)
                role_counts['Software Related']['original_roles'].append(role)
            elif 'AI' in role:
                role_counts['AI Related']['company_count'] += 1
                role_counts['AI Related']['company_names'].append(company_name)
                role_counts['AI Related']['original_roles'].append(role)
            elif 'Data' in role or 'Analyst' in role:
                role_counts['Data Science']['company_count'] += 1
                role_counts['Data Science']['company_names'].append(company_name)
                role_counts['Data Science']['original_roles'].append(role)
            else:
                role_counts['Others']['company_count'] += 1
                role_counts['Others']['company_names'].append(company_name)
                role_counts['Others']['original_roles'].append(role)

        # Prepare structured data for role counts
        role_data = [
            {'role_name': role, 'company_count': data['company_count'],
             'company_names': data['company_names'], 'original_roles': data['original_roles']}
            for role, data in role_counts.items()
        ]

        # Prepare data for selected students and round-wise selection
        selected_data = []
        rounds_data = []

        for placement in placements:
            company_name = placement.get('Company Name', 'Unknown Company')

            # Fetching student selection data
            selected_students = placement.get('Students Selected', [])
            selected_names = placement.get('Students Selected Names')
            if selected_students:
                selected_data.append({
                    'company_name': company_name,
                    'students_selected': selected_students,
                    'selected_names': selected_names 
                })

            # Fetching round-wise selection data
            first_round = placement.get('Students 1st Round', 0)
            second_round = placement.get('Students 2nd Round', 0)
            final_round = placement.get('Students Final Round', 0)
            
            rounds_data.append({
                'company_name': company_name,
                'first_round': first_round,
                'second_round': second_round,
                'final_round': final_round
            })
        print(selected_data)

        # Prepare context data
        context = {
            'total_companies': total_companies,
            'dream_non_dream_count': dict(dream_non_dream_count),
            'offer_type_count': dict(offer_type_count),
            'role_data': role_data,
            'selected_data': selected_data,  # Pass the selected students data
            'rounds_data': rounds_data       # Pass the round-wise data
        }

        return render(request, 'accounts/view_details.html', context)

    except Exception as e:
        messages.error(request, f"Error retrieving details: {e}")
        return redirect('view_details')
@role_required(allowed_roles=['Student'])
def student_details_view(request):
    if request.method == 'POST':
        form = StudentDetailsForm(request.POST)
        if form.is_valid():
            roll_number = form.cleaned_data['roll_number']
            name = form.cleaned_data['name']
            dept = form.cleaned_data['dept']
            company = form.cleaned_data['company']
            role = form.cleaned_data['role']
            internship_type = form.cleaned_data['internship_type']
            campus = form.cleaned_data['campus']

            # Save student details to the 'Students' collection in MongoDB
            try:
                students_collection = db['Student']  # The MongoDB collection for students
                students_collection.insert_one({
                    'Roll Number': roll_number,
                    'Name': name,
                    'Department': dept,

                    'Company': company,
                    'Role': role,
                    'Internship Type': internship_type,
                    'Campus Type': campus
                })
                messages.success(request, "Student details added successfully!")
                return redirect('student_dashboard')
            except Exception as e:
                messages.error(request, f"Error saving student details: {e}")
    else:
        form = StudentDetailsForm()

    return render(request, 'accounts/student_details.html', {'form': form})


def teacher_dashboard(request):
    return render(request, 'accounts/teacher_dashboard.html')

def placement_coordinator_dashboard(request):
    return render(request, 'accounts/placement_coordinator_dashboard.html')

def student_dashboard(request):
    return render(request, 'accounts/student_dashboard.html')
class StudentForm(forms.Form):
    
    username = forms.CharField(max_length=100, label='Roll Number')  # Username as Roll Number
    name = forms.CharField(max_length=100, label='Name')
    dept = forms.CharField(max_length=100, label='Department')
    company = forms.CharField(max_length=100, label='Company')
    role = forms.CharField(max_length=100, label='Role')
    internship_type = forms.ChoiceField(choices=[('Intern', 'Intern'), ('Intern+PBC', 'Intern+PBC')], label='Internship Type')
    campus = forms.ChoiceField(choices=[('On Campus', 'On Campus'), ('Off Campus', 'Off Campus')], label='Campus')

# View for submitting student details
@role_required(allowed_roles=['student'])
def submit_student_form_view(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student_data = {
                'Roll Number': form.cleaned_data['username'],
                'Name': form.cleaned_data['name'],
                'Department': form.cleaned_data['dept'],
                'Company': form.cleaned_data['company'],
                'Role': form.cleaned_data['role'],
                'Internship Type': form.cleaned_data['internship_type'],
                'Campus': form.cleaned_data['campus']
            }
            try:
                # Insert student details into the Students collection in MongoDB
                students_collection.insert_one(student_data)
                messages.success(request, "Student details submitted successfully!")
                return redirect('student_dashboard')
            except Exception as e:
                messages.error(request, f"Error saving student details: {e}")
    else:
        form = StudentForm()

    return render(request, 'accounts/submit_student_form.html', {'form': form})



# Feedback page redirection from the dashboard button
def submit_feedback_view(request):
    return redirect('submit_student_form_view')

def home_view(request):
    return redirect('login')


