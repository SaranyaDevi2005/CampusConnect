# your_app/forms.py

from django import forms

# Choices for the login form
ROLE_CHOICES = [
    ('teacher', 'Teacher'),
    ('placement cordinator', 'Placement Cordinator'),
    ('student', 'Student'),
]

# Form for Login
class LoginForm(forms.Form):
    username = forms.CharField(
        label='Username',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your username'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label='Role'
    )

# Form for adding a company
class AddCompanyForm(forms.Form):
    company_name = forms.CharField(
        label='Company Name',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter company name'})
    )
    dream_non_dream = forms.ChoiceField(
        choices=[('DREAM', 'DREAM'), ('NON-DREAM', 'NON-DREAM')],
        label='DREAM/NON-DREAM'
    )
    offer_type = forms.ChoiceField(
        choices=[('MSC', 'MSC'), ('Engineering', 'Engineering'), ('Both', 'Both')],
        label='Offer For'
    )
    role = forms.CharField(
        label='Role',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter role'})
    )

# Form for adding placement details
class AddPlacementDetailsForm(forms.Form):
    company_name = forms.ChoiceField(
        label='Company Name',
        choices=[],  # Placeholder, choices will be populated in the view
        widget=forms.Select
    )
    students_1st_round = forms.IntegerField(
        label='No. of Students Selected in 1st Round',
        min_value=0
    )
    students_2nd_round = forms.IntegerField(
        label='No. of Students Selected in 2nd Round',
        min_value=0
    )
    students_final_round = forms.IntegerField(
        label='No. of Students in Final Round',
        min_value=0
    )
    students_final_names = forms.CharField(
        label='Names of Students in Final Round',
        max_length=1000,
        widget=forms.TextInput(attrs={'placeholder': 'commas separated'})
    )
    students_selected = forms.IntegerField(
        label='No. of Students Selected',
        min_value=0
    )
    students_selected_names = forms.CharField(
        label='Names of Students Selected',
        max_length=1000,
        widget=forms.TextInput(attrs={'placeholder': 'commas separated'})
    )

# Form for adding a Placement Coordinator
class AddPlacementCoordinatorForm(forms.Form):
    username = forms.CharField(
        label='Username',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter username'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'})
    )

class AddStudentForm(forms.Form):
    username = forms.CharField(
        label='Username',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter username'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'})
    )    

# Form for student details
class StudentDetailsForm(forms.Form):
    roll_number = forms.CharField(
        label='Roll Number',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter roll number'})
    )
    name = forms.CharField(
        label='Name',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter full name'})
    )
    dept = forms.CharField(
        label='Department',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter department'})
    )
    company = forms.CharField(
        label='Company',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter company name'})
    )
    role = forms.CharField(
        label='Role',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter job role'})
    )
    internship_type = forms.ChoiceField(
        label='Internship Type',
        choices=[('Intern', 'Intern'), ('Intern+PBC', 'Intern + PBC')],
        widget=forms.Select
    )
    campus = forms.ChoiceField(
        label='Campus Type',
        choices=[('On Campus', 'On Campus'), ('Off Campus', 'Off Campus')],
        widget=forms.Select
    )