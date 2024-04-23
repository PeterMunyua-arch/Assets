from django import forms
from .models import InventoryItem, Asset, Employee, Company, Transaction, AssetAllocation, AssetReturn, Disposal



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
    class Meta:
        model = Asset
        fields = ['name', 'model', 'type', 'office', 'office_licence', 'os', 'os_licence', 'specs', 'purchase_price', 'purchase_date', 'serial_number', 'accessories', 'ip', 'company']


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
        fields = ['company', 'first_name', 'last_name', 'department', 'email', 'phone_number', 'employee_id']



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
    class Meta:
        model = AssetAllocation
        fields = ['asset', 'serial_number','employee_allocated', 'allocation_date', 'return_date', 'asset_status']

class AssetReturnForm(forms.ModelForm):
    class Meta:
        model = AssetReturn
        fields = ['asset', 'serial_number', 'employee_returning', 'return_date', 'asset_status']



class DisposalForm(forms.ModelForm):
    class Meta:
        model = Disposal
        fields = ['asset', 'serial_number', 'disposal_reason', 'disposal_date']
        

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

