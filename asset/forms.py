from django import forms
from .models import InventoryItem, Asset, Employee, Company, Transaction, AssetAllocation, AssetReturn, Damaged



#class AddForm(forms.Form):
   # name = forms.CharField(label='Asset Name', max_length=100)
    #model = forms.CharField(label='Model Name',max_length=100)
    #specs = forms.CharField(label='Specs', widget=forms.Textarea)
   # ram = forms.CharField(label='Ram', max_length=20)
    #purchase_price = forms.DecimalField(label='Purchase Price', max_digits=10, decimal_places=2)
    #purchase_date = forms.DateField(label='Purchase Date')
  #  serial_number = forms.CharField(label='Serial Number',max_length=100)
   # company = forms.ModelChoiceField(queryset=Company.objects.all(), label='Company')

#class EmployeeForm(forms.Form):
   # company = forms.ModelChoiceField(queryset=Company.objects.all(), label='Company')
   # first_name = forms.CharField(label='First Name', max_length=50)
    #last_name = forms.CharField(label='Last Name', max_length=50)
   # department = forms.CharField(label='Department', max_length=100)
   # email = forms.EmailField(label='Email')
   # phone_number = forms.CharField(label='Phone Number', max_length=20)
   # employee_id = forms.CharField(label='Employee Id', max_length=20)

   # forms.py


class AddForm(forms.ModelForm):
    applications = forms.MultipleChoiceField(
        choices=Asset.APPLICATIONS_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Business Applications"
    )
    
    class Meta:
        model = Asset
        fields = [
            'name', 'model', 'type', 'office', 'office_licence', 'os', 'os_licence', 
            'specs', 'imei_number', 'processor', 'ram', 'ssd_capacity', 'hdd_capacity', 
            'purchase_price', 'purchase_date', 'serial_number', 'accessories', 'ip', 
            'company', 'applications', 'other_applications'
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'other_applications': forms.Textarea(attrs={'rows': 3, 'placeholder': 'List any additional software or applications not included in the checklist above'}),
        }
    
    def save(self, commit=True):
        asset = super().save(commit=False)
        
        # Handle applications
        applications = self.cleaned_data.get('applications', [])
        apps_dict = {}
        for app in applications:
            apps_dict[app] = True
        
        asset.applications = apps_dict
        
        if commit:
            asset.save()
        
        return asset
    
    def clean_imei_number(self):
        imei = self.cleaned_data.get('imei_number')
        if imei:
            # Remove any non-digit characters
            imei = ''.join(filter(str.isdigit, imei))
            if len(imei) not in [15, 16]:
                raise forms.ValidationError("IMEI number must be 15 or 16 digits long")
        return imei
    
class AddTablet(AddForm):
    tablet_specific_field = forms.CharField(max_length=50)

class AddMobile(AddForm):
    mobile_specific_field = forms.CharField(max_length=50)

class AddDesktop(AddForm):
    office = forms.CharField(max_length=50)
    office_licence = forms.CharField(max_length=50)
    os = forms.CharField(max_length=100)
    os_licence = forms.CharField(max_length=100)

class AddLaptop(AddForm):
    office = forms.CharField(max_length=50)
    office_licence = forms.CharField(max_length=50)
    os = forms.CharField(max_length=100)
    os_licence = forms.CharField(max_length=100)

class AddServer(AddForm):
    server_specific_field = forms.CharField(max_length=50)

class AddPrinter(AddForm):
    printer_specific_field = forms.CharField(max_length=50)

    
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['company', 'first_name', 'last_name', 'department', 'email', 'phone_number']



class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['asset', 'asset_name', 'serial_number', 'assigned_to', 'assignment_date', 'status']
        widgets = {'assignment_date': forms.DateInput(attrs={'type': 'date'})}

class ReturnForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['asset', 'asset_name', 'serial_number', 'return_date', 'status']
        widgets = {'return_date': forms.DateInput(attrs={'type': 'date'})}

class AssetAllocationForm(forms.ModelForm):
    applications = forms.MultipleChoiceField(
        choices=Asset.APPLICATIONS_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Include Applications"
    )
    
    include_all_applications = forms.BooleanField(
        required=False,
        initial=True,
        label="Include all asset applications"
    )
    
    class Meta:
        model = AssetAllocation
        fields = ['asset', 'employee_allocated', 'allocation_date', 'return_date', 'asset_status', 
                 'applications', 'include_all_applications']
        widgets = {
            'allocation_date': forms.DateInput(attrs={'type': 'date'}),
            'return_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial applications based on asset if provided
        if 'asset' in self.initial:
            asset_id = self.initial['asset']
            try:
                asset = Asset.objects.get(id=asset_id)
                # Pre-select applications that are available on the asset
                available_apps = [app for app, included in asset.applications.items() if included]
                self.fields['applications'].initial = available_apps
            except Asset.DoesNotExist:
                pass
    
    def save(self, commit=True):
        allocation = super().save(commit=False)
        
        if self.cleaned_data.get('include_all_applications', True):
            # Include all applications from the asset
            allocation.allocated_applications = allocation.asset.applications
        else:
            # Include only selected applications
            selected_apps = self.cleaned_data.get('applications', [])
            apps_dict = {}
            for app in selected_apps:
                apps_dict[app] = True
            allocation.allocated_applications = apps_dict
        
        if commit:
            allocation.save()
        
        return allocation
    

class AssetReturnForm(forms.ModelForm):
    class Meta:
        model = AssetReturn
        fields = ['asset', 'employee_returning', 'return_date', 'asset_status']



class DisposalForm(forms.ModelForm):
    class Meta:
        model = Damaged
        fields = ['asset', 'damage_reason', 'damage_date']
        

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model=User
        fields=['first_name','email','username','password1','password2']
        

    def __init__(self,*args, **kwargs):
        super(UserCreationForm,self).__init__(*args, **kwargs)
        for name,field in self.fields.items():
            field.widget.attrs.update({'class':'input'})


# forms.py
from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)




from django import forms

class AssetImportForm(forms.Form):
    file = forms.FileField(label='Excel File', widget=forms.FileInput(attrs={
        'accept': '.xlsx, .xls, .csv',
        'class': 'custom-file-input'
    }))

class UserImportForm(forms.Form):
    file = forms.FileField(label='Excel File', widget=forms.FileInput(attrs={
        'accept': '.xlsx, .xls, .csv',
        'class': 'custom-file-input'
    }))



# In your forms.py
from django import forms
import pandas as pd
import chardet

class MassUploadForm(forms.Form):
    UPLOAD_TYPE_CHOICES = [
        ('asset', 'Assets'),
        ('employee', 'Employees'),
        ('allocation', 'Asset Allocations'),
    ]
    
    upload_type = forms.ChoiceField(
        choices=UPLOAD_TYPE_CHOICES,
        required=True,
        label="What do you want to upload?"
    )
    
    file = forms.FileField(
        label='Upload File',
        help_text='Supported formats: CSV, Excel (.xlsx, .xls)',
        widget=forms.FileInput(attrs={
            'accept': '.csv,.xlsx,.xls',
            'class': 'custom-file-input'
        })
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file extension
            ext = file.name.split('.')[-1].lower()
            if ext not in ['csv', 'xlsx', 'xls']:
                raise forms.ValidationError("Unsupported file format. Please upload CSV or Excel files.")
            
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size too large. Maximum size is 10MB.")
                
        return file