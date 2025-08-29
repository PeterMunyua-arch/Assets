from django.shortcuts import render, get_object_or_404, redirect
from .models import  Employee, Asset, Transaction, AssetAllocation, AssetReturn, Company, Damaged
from .forms import AssignmentForm, ReturnForm, AddForm, EmployeeForm, AssetAllocationForm, AssetReturnForm, DisposalForm
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from datetime import timedelta, datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from .models import Asset, Company
from .forms import AddTablet, AddMobile, AddDesktop, AddLaptop, AddServer, AddPrinter
from django.shortcuts import render, redirect
from .models import Asset 
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.shortcuts import render
from .models import Asset, Employee, AssetAllocation
from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import render, redirect
from django.db.models import Q, Count
from django.db import models
from django.db.models import Q, Prefetch
from django.db.models import Count
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import HttpResponseRedirect
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Count
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
import csv
from django.template.loader import render_to_string
import tempfile
import openpyxl
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AssetImportForm, UserImportForm
import pandas as pd
from django.views.generic import ListView
import pandas as pd
import chardet
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db import transaction
from .models import Asset, Employee, AssetAllocation, Company
from .forms import MassUploadForm
import pandas as pd
from django.http import HttpResponse
from io import BytesIO
from django.http import HttpResponse
from django.db.models import Count, Q
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
import pandas as pd
from io import BytesIO
from datetime import datetime


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'asset/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'asset/signup.html', {'form': form})

def password_change_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to change your password.")
        return redirect('login')
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update session to prevent logging out
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been changed successfully!")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'asset/password_change.html', {'form': form})

@login_required
def home(request):
    total_assets = Asset.objects.count()
    allocated_assets = Asset.objects.filter(is_allocated=True).count()
    unallocated_assets = total_assets - allocated_assets
    total_employees = Employee.objects.count()
    
    # Count assets by type
    laptop_count = Asset.objects.filter(type='Laptop').count()
    desktop_count = Asset.objects.filter(type='Desktop').count()
    mobile_count = Asset.objects.filter(type='Mobile').count()
    tablet_count = Asset.objects.filter(type='Tablet').count()
    printer_count = Asset.objects.filter(type='Printer').count()
    other_count = Asset.objects.filter(type='Other').count()
    
    # Allocation status counts
    assigned_assets = allocated_assets
    available_assets = unallocated_assets
    
    context = {
        'total_assets': total_assets,
        'allocated_assets': allocated_assets,
        'unallocated_assets': unallocated_assets,
        'total_employees': total_employees,
        'laptop_count': laptop_count,
        'desktop_count': desktop_count,
        'mobile_count': mobile_count,
        'tablet_count': tablet_count,
        'printer_count': printer_count,
        'other_count': other_count,
        'assigned_assets': assigned_assets,
        'available_assets': available_assets,
        
    }

    return render(request, 'asset/home.html', context)

@login_required
def dashboard(request):
    # Basic counts
    total_assets = Asset.objects.count()
    allocated_assets = Asset.objects.filter(is_allocated=True).count()
    unallocated_assets = total_assets - allocated_assets
    damaged_assets = Damaged.objects.count()
    
    # Recent activity
    recent_allocations = AssetAllocation.objects.select_related(
        'asset', 'employee_allocated'
    ).order_by('-allocation_date')[:5]
    
    recent_returns = AssetReturn.objects.select_related(
        'asset', 'employee_returning'
    ).order_by('-return_date')[:5]
    
    context = {
        'total_assets': total_assets,
        'allocated_assets': allocated_assets,
        'unallocated_assets': unallocated_assets,
        'damaged_assets': damaged_assets,
        'recent_allocations': recent_allocations,
        'recent_returns': recent_returns,
    }
    return render(request, 'asset/dashboard.html', context)

@login_required
@login_required
def asset_allocation_form(request):
    if request.method == 'POST':
        form = AssetAllocationForm(request.POST)
        if form.is_valid():
            allocation = form.save(commit=False)
            allocation.allocation_date = timezone.now().date()
            allocation.save()
            
            # Redirect to form generation after successful allocation
            return redirect('generate_allocation_form', allocation_id=allocation.id)
    else:
        form = AssetAllocationForm()
        # Pre-fill asset if provided in GET parameters
        asset_id = request.GET.get('asset')
        if asset_id:
            try:
                asset = Asset.objects.get(id=asset_id)
                form.fields['asset'].initial = asset
                # Pre-select applications based on asset
                available_apps = [app for app, included in asset.applications.items() if included]
                form.fields['applications'].initial = available_apps
            except Asset.DoesNotExist:
                pass
    
    return render(request, 'asset/asset_allocation_form.html', {'form': form})

@login_required
def generate_allocation_form(request, allocation_id):
    allocation = get_object_or_404(AssetAllocation, id=allocation_id)
    asset = allocation.asset
    
    # Determine which template to use based on asset type
    if asset.type in ['Laptop', 'Desktop']:
        template_name = 'asset/computer_allocation_form.html'
    elif asset.type in ['Tablet', 'Mobile']:
        template_name = 'asset/mobile_allocation_form.html'
    else:
        # Default to computer form for other types
        template_name = 'asset/computer_allocation_form.html'
    
    context = {
        'allocation': allocation,
        'asset': asset,
    }
    
    return render(request, template_name, context)


@login_required
def asset_return_form(request):
    if request.method == 'POST':
        form = AssetReturnForm(request.POST)
        if form.is_valid():
            allocation = form.save()  # Save the allocation
            return redirect('assetreturn_detail', asset_id=allocation.pk)   # Redirect to asset return detail page
    else:
        form = AssetReturnForm()
    return render(request, 'asset/asset_allocation_form.html', {'form': form})


def assetreturn_detail(request, asset_id):
    asset_return = get_object_or_404(AssetReturn, pk=asset_id)
    return render(request, 'asset/assetreturn_detail.html', {'asset_return': asset_return})

def success_page(request, success_message=None):
    return render(request, 'asset/success.html', {'success_message': success_message})

def assign_asset(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            serial_number = form.cleaned_data['serial_number']
            if Transaction.objects.filter(serial_number=serial_number, return_date__isnull=True).exists():
                return render(request, 'asset/assign_asset.html', {'form': form, 'error_message': 'Asset is already assigned.'})
            else:
                form.save()
                return redirect('asset_list')  # Redirect to asset list page or wherever you want
    else:
        form = AssignmentForm()
    return render(request, 'asset/assign_asset.html', {'form': form})

@login_required
def add_asset(request):
    if request.method == 'POST':
        form = AddForm(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.company = Company.objects.first()  # Example: Assign a company
            asset.save()
            return redirect('add_asset')  # Redirect to asset list page or another page
    else:
        form = AddForm()

    return render(request, 'asset/add_asset.html', {'form': form})

@login_required
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to the database
            return redirect('add_employee')  # Redirect to success page
    else:
        form = EmployeeForm()
    return render(request, 'asset/add_employee.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to the login page after successful signup
    else:
        form = UserCreationForm()
    return render(request, 'asset/signup.html', {'form': form})



def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to the home page after successful password change
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'asset/password_change.html', {'form': form})



def password_reset_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('password_reset_done')  # Redirect to the password reset done page
    else:
        form = PasswordResetForm()
    return render(request, 'asset/password_reset.html', {'form': form})

def password_reset_done_view(request):
    return render(request, 'asset/password_reset_done.html')


def dashboard(request):
    total_assets = Asset.objects.count()
    assigned_assets = Asset.objects.filter(is_allocated=True).count()
    

    context = {
        'total_assets': total_assets,
        'assigned_assets': assigned_assets,
    }
    return render(request, 'asset/dashboard.html', context)


def asset_disposal(request):
    if request.method == 'POST':
        form = DisposalForm(request.POST)
        if form.is_valid():
            disposal = form.save()
            # Perform any additional actions after disposal
            return redirect('home')  # Redirect to dashboard or another page
    else:
        form = DisposalForm()

    context = {'form': form}
    return render(request, 'asset/disposal.html', context)



def asset_list(request):
    assets = Asset.objects.all()  # Retrieve all assets from the database
    return render(request, 'assets/asset_list.html', {'assets': assets})

@login_required
def return_asset(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    
    if request.method == 'POST':
        form = ReturnForm(request.POST)
        if form.is_valid():
            # Create the return record
            return_record = form.save(commit=False)
            return_record.asset = asset
            return_record.return_date = timezone.now().date()
            return_record.save()
            
            messages.success(request, f"Asset {asset.serial_number} has been successfully returned.")
            return redirect('asset_detail', asset_id=asset.id)
    else:
        # Get current allocation to pre-populate employee
        current_allocation = AssetAllocation.objects.filter(
            asset=asset,
            return_date__isnull=True
        ).first()
        
        initial = {
            'asset': asset,
            'employee_returning': current_allocation.employee_allocated if current_allocation else None,
        }
        
        form = ReturnForm(initial=initial)
    
    return render(request, 'asset/return_asset.html', {
        'form': form,
        'asset': asset,
    })


def signup(request):
    if request.user.is_authenticated:
        return redirect('signin')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            # login(request, user)
            return redirect('/signin')
        else:
            return render(request, 'asset/signup.html', {'form': form})
    else:
        form = CustomUserCreationForm()
        return render(request, 'aseet/signup.html', {'form': form})


def signin(request):
    if request.user.is_authenticated:
        return render(request, 'asset/home.html')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home') #profile
        else:
            msg = 'Error Login'
            form = AuthenticationForm(request.POST)
            return render(request, 'asset/login.html', {'form': form, 'msg': msg})
    else:
        form = AuthenticationForm()
        return render(request, 'asset/login.html', {'form': form})

def profile(request): 
    return render(request, 'asset/profile.html')


def search(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return render(request, 'asset/search_results.html', {'query': query})
    
    # Prefetch current allocations for assets
    current_allocations = AssetAllocation.objects.filter(
        return_date__isnull=True
    ).select_related('employee_allocated')
    
    # Search for assets with prefetched allocations
    assets = Asset.objects.filter(
        Q(serial_number__icontains=query) |
        Q(name__icontains=query) |
        Q(model__icontains=query) |
        Q(type__icontains=query)
    ).prefetch_related(
        Prefetch('assetallocation_set', queryset=current_allocations, to_attr='current_allocation')
    ).distinct()
    
    # Search for employees with annotated current asset count
    employees = Employee.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(department__icontains=query) |
        Q(email__icontains=query)
    ).annotate(
        current_assets_count=Count(
            'assetallocation',
            filter=Q(assetallocation__return_date__isnull=True)
        )
    ).distinct()
    
    context = {
        'query': query,
        'assets': assets,
        'employees': employees,
    }
    
    return render(request, 'asset/search_results.html', context)


def asset_detail(request, asset_id):
    asset = get_object_or_404(Asset, pk=asset_id)
    
    # Get all allocations ordered by date
    allocations = AssetAllocation.objects.filter(asset=asset).order_by('-allocation_date')
    
    # Get all returns ordered by date
    returns = AssetReturn.objects.filter(asset=asset).order_by('-return_date')
    
    # Determine current status
    current_allocation = None
    if asset.is_allocated and not asset.is_returned:
        current_allocation = AssetAllocation.objects.filter(
            asset=asset,
            return_date__isnull=True
        ).first()
    
    context = {
        'asset': asset,
        'allocations': allocations,
        'returns': returns,
        'current_allocation': current_allocation,
    }
    
    return render(request, 'asset/asset_detail.html', context)


def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    allocations = AssetAllocation.objects.filter(employee_allocated=employee).order_by('-allocation_date')
    returns = AssetReturn.objects.filter(employee_returning=employee).order_by('-return_date')
    
    context = {
        'employee': employee,
        'allocations': allocations,
        'returns': returns,
        'current_assets': allocations.filter(return_date__isnull=True),
    }
    
    return render(request, 'asset/employee_detail.html', context)

class AllAssetsReport(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'asset/reports/all_assets.html'
    context_object_name = 'assets'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('company').order_by('type', 'serial_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_title'] = "All Assets Report"
        context['total_count'] = self.get_queryset().count()
        return context

class AllocatedAssetsReport(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'asset/reports/allocated_assets.html'
    context_object_name = 'assets'
    paginate_by = 25
    
    def get_queryset(self):
        return Asset.objects.filter(
            is_allocated=True
        ).select_related('company').prefetch_related(
            'assetallocation_set'
        ).order_by('type', 'serial_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_title'] = "Allocated Assets Report"
        context['total_count'] = self.get_queryset().count()
        return context

class UnallocatedAssetsReport(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'asset/reports/unallocated_assets.html'
    context_object_name = 'assets'
    paginate_by = 25
    
    def get_queryset(self):
        return Asset.objects.filter(
            is_allocated=False
        ).select_related('company').order_by('type', 'serial_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_title'] = "Unallocated Assets Report"
        context['total_count'] = self.get_queryset().count()
        return context


def export_assets(request):
    format = request.GET.get('format', 'csv')
    assets = Asset.objects.all().select_related('company')
    
    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="assets_{}.csv"'.format(
            datetime.now().strftime("%Y%m%d")
        )
        
        writer = csv.writer(response)
        writer.writerow([
            'Serial Number', 'Asset Type', 'Model', 'Company', 
            'Status', 'Purchase Date', 'Price'
        ])
        
        for asset in assets:
            status = "Allocated" if asset.is_allocated else "Unallocated"
            writer.writerow([
                asset.serial_number,
                asset.get_type_display(),
                asset.model,
                asset.company.name,
                status,
                asset.purchase_date.strftime("%Y-%m-%d") if asset.purchase_date else "",
                str(asset.purchase_price) if asset.purchase_price else ""
            ])
            
        return response
        
    elif format == 'excel':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="assets_{}.xlsx"'.format(
            datetime.now().strftime("%Y%m%d")
        )
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Assets"
        
        headers = [
            'Serial Number', 'Asset Type', 'Model', 'Company', 
            'Status', 'Purchase Date', 'Price'
        ]
        ws.append(headers)
        
        for asset in assets:
            status = "Allocated" if asset.is_allocated else "Unallocated"
            ws.append([
                asset.serial_number,
                asset.get_type_display(),
                asset.model,
                asset.company.name,
                status,
                asset.purchase_date,
                asset.purchase_price
            ])
            
        wb.save(response)
        return response
        
    elif format == 'pdf':
        html_string = render_to_string('asset/reports/export_pdf.html', {
            'assets': assets,
            'date': datetime.now().strftime("%B %d, %Y")
        })
        
        html = HTML(string=html_string)
        result = html.write_pdf()
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="assets_{}.pdf"'.format(
            datetime.now().strftime("%Y%m%d")
        )
        response.write(result)
        
        return response
        
    return redirect('dashboard')


class AssetTypeReportView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'asset/reports/asset_type_report.html'
    context_object_name = 'assets'
    paginate_by = 25
    
    def get_queryset(self):
        asset_type = self.kwargs['type']
        return Asset.objects.filter(
            type=asset_type
        ).select_related('company').order_by('serial_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asset_type = self.kwargs['type']
        context['report_title'] = f"{asset_type.capitalize()} Assets Report"
        context['asset_type'] = asset_type
        context['total_count'] = self.get_queryset().count()
        return context


def import_assets(request):
    if request.method == 'POST':
        form = AssetImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                df = pd.read_excel(request.FILES['file'])
                # Process each row
                for index, row in df.iterrows():
                    Asset.objects.create(
                        name=row.get('Name', ''),
                        serial_number=row.get('Serial Number', ''),
                        type=row.get('Type', 'laptop'),
                        model=row.get('Model', ''),
                        company=Company.objects.get_or_create(name=row.get('Company', 'Default Company'))[0],
                        # Add other fields as needed
                    )
                messages.success(request, f'Successfully imported {len(df)} assets')
                return redirect('asset_list')
            except Exception as e:
                messages.error(request, f'Error importing file: {str(e)}')
    else:
        form = AssetImportForm()
    return render(request, 'asset/import_form.html', {'form': form, 'title': 'Import Assets'})

def import_users(request):
    if request.method == 'POST':
        form = UserImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                df = pd.read_excel(request.FILES['file'])
                for index, row in df.iterrows():
                    Employee.objects.create(
                        first_name=row.get('First Name', ''),
                        last_name=row.get('Last Name', ''),
                        email=row.get('Email', ''),
                        department=row.get('Department', ''),
                        company=Company.objects.get_or_create(name=row.get('Company', 'Default Company'))[0],
                        # Add other fields as needed
                    )
                messages.success(request, f'Successfully imported {len(df)} users')
                return redirect('employee_list')
            except Exception as e:
                messages.error(request, f'Error importing file: {str(e)}')
    else:
        form = UserImportForm()
    return render(request, 'asset/import_form.html', {'form': form, 'title': 'Import Users'})



@login_required
def mass_upload(request):
    if request.method == 'POST':
        form = MassUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload_type = form.cleaned_data['upload_type']
            file = form.cleaned_data['file']
            
            try:
                # Process the file based on type
                if upload_type == 'asset':
                    result = process_asset_upload(file)
                elif upload_type == 'employee':
                    result = process_employee_upload(file)
                elif upload_type == 'allocation':
                    result = process_allocation_upload(file)
                
                messages.success(request, result['message'])
                return redirect('mass_upload')
                
            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
                return render(request, 'asset/mass_upload.html', {'form': form})
    else:
        form = MassUploadForm()
    
    return render(request, 'asset/mass_upload.html', {'form': form})


def read_uploaded_file(file):
    """Read uploaded file and return DataFrame"""
    ext = file.name.split('.')[-1].lower()
    
    if ext == 'csv':
        # Detect encoding for CSV files
        raw_data = file.read()
        detected = chardet.detect(raw_data)
        encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
        
        # Reset file pointer
        file.seek(0)
        
        # Read CSV with detected encoding
        return pd.read_csv(file, encoding=encoding)
    
    elif ext in ['xlsx', 'xls']:
        return pd.read_excel(file)
    
    else:
        raise ValueError("Unsupported file format")

def process_asset_upload(file):
    """Process asset upload from CSV/Excel"""
    df = read_uploaded_file(file)
    
    # Normalize column names (remove spaces, lowercase, etc.)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    required_columns = ['serial_number', 'name']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    success_count = 0
    error_count = 0
    errors = []
    
    with transaction.atomic():
        for index, row in df.iterrows():
            try:
                asset_data = {}
                
                # Map CSV columns to model fields
                field_mapping = Asset.get_import_fields()
                for csv_col, model_field in field_mapping.items():
                    if csv_col in df.columns and pd.notna(row.get(csv_col)):
                        asset_data[model_field] = row[csv_col]
                
                # Handle company field (could be name or ID)
                if 'company' in asset_data:
                    company_value = asset_data['company']
                    if isinstance(company_value, str):
                        # Try to find company by name
                        company, created = Company.objects.get_or_create(
                            name=company_value,
                            defaults={'location': 'Unknown'}
                        )
                        asset_data['company'] = company
                    elif isinstance(company_value, (int, float)):
                        # Try to find company by ID
                        try:
                            asset_data['company'] = Company.objects.get(id=int(company_value))
                        except Company.DoesNotExist:
                            errors.append(f"Row {index+2}: Company with ID {company_value} not found")
                            error_count += 1
                            continue
                
                # Check if asset already exists
                serial_number = asset_data.get('serial_number')
                if Asset.objects.filter(serial_number=serial_number).exists():
                    asset = Asset.objects.get(serial_number=serial_number)
                    for key, value in asset_data.items():
                        setattr(asset, key, value)
                    asset.save()
                else:
                    asset = Asset.objects.create(**asset_data)
                
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {index+2}: {str(e)}")
                error_count += 1
    
    message = f"Processed {success_count} assets successfully."
    if error_count > 0:
        message += f" {error_count} errors occurred."
        if errors:
            message += " First error: " + errors[0]
    
    return {'message': message, 'success_count': success_count, 'error_count': error_count, 'errors': errors}

def process_employee_upload(file):
    """Process employee upload from CSV/Excel"""
    df = read_uploaded_file(file)
    
    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    required_columns = ['first_name', 'last_name', 'email', 'company']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    success_count = 0
    error_count = 0
    errors = []
    
    with transaction.atomic():
        for index, row in df.iterrows():
            try:
                employee_data = {}
                
                # Map CSV columns to model fields
                field_mapping = Employee.get_import_fields()
                for csv_col, model_field in field_mapping.items():
                    if csv_col in df.columns and pd.notna(row.get(csv_col)):
                        employee_data[model_field] = row[csv_col]
                
                # Handle company field
                if 'company' in employee_data:
                    company_value = employee_data['company']
                    if isinstance(company_value, str):
                        company, created = Company.objects.get_or_create(
                            name=company_value,
                            defaults={'location': 'Unknown'}
                        )
                        employee_data['company'] = company
                    elif isinstance(company_value, (int, float)):
                        try:
                            employee_data['company'] = Company.objects.get(id=int(company_value))
                        except Company.DoesNotExist:
                            errors.append(f"Row {index+2}: Company with ID {company_value} not found")
                            error_count += 1
                            continue
                
                # Check if employee already exists
                email = employee_data.get('email')
                if Employee.objects.filter(email=email).exists():
                    employee = Employee.objects.get(email=email)
                    for key, value in employee_data.items():
                        setattr(employee, key, value)
                    employee.save()
                else:
                    employee = Employee.objects.create(**employee_data)
                
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {index+2}: {str(e)}")
                error_count += 1
    
    message = f"Processed {success_count} employees successfully."
    if error_count > 0:
        message += f" {error_count} errors occurred."
        if errors:
            message += " First error: " + errors[0]
    
    return {'message': message, 'success_count': success_count, 'error_count': error_count, 'errors': errors}

def process_allocation_upload(file):
    """Process allocation upload from CSV/Excel"""
    df = read_uploaded_file(file)
    
    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    required_columns = ['asset_serial_number', 'employee_email', 'allocation_date']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    success_count = 0
    error_count = 0
    errors = []
    
    with transaction.atomic():
        for index, row in df.iterrows():
            try:
                allocation_data = {}
                
                # Map CSV columns to model fields
                field_mapping = AssetAllocation.get_import_fields()
                for csv_col, model_field in field_mapping.items():
                    if csv_col in df.columns and pd.notna(row.get(csv_col)):
                        allocation_data[model_field] = row[csv_col]
                
                # Handle asset field (by serial number)
                serial_number = allocation_data.get('asset')
                try:
                    asset = Asset.objects.get(serial_number=serial_number)
                    allocation_data['asset'] = asset
                except Asset.DoesNotExist:
                    errors.append(f"Row {index+2}: Asset with serial number {serial_number} not found")
                    error_count += 1
                    continue
                
                # Handle employee field (by email)
                email = allocation_data.get('employee_allocated')
                try:
                    employee = Employee.objects.get(email=email)
                    allocation_data['employee_allocated'] = employee
                except Employee.DoesNotExist:
                    errors.append(f"Row {index+2}: Employee with email {email} not found")
                    error_count += 1
                    continue
                
                # Handle date fields
                for date_field in ['allocation_date', 'return_date']:
                    if date_field in allocation_data and pd.notna(allocation_data[date_field]):
                        if isinstance(allocation_data[date_field], str):
                            try:
                                allocation_data[date_field] = datetime.strptime(
                                    allocation_data[date_field], '%Y-%m-%d'
                                ).date()
                            except ValueError:
                                try:
                                    allocation_data[date_field] = datetime.strptime(
                                        allocation_data[date_field], '%m/%d/%Y'
                                    ).date()
                                except ValueError:
                                    errors.append(f"Row {index+2}: Invalid date format for {date_field}")
                                    error_count += 1
                                    continue
                
                # Create allocation
                allocation = AssetAllocation.objects.create(**allocation_data)
                
                # Update asset status
                asset.is_allocated = True
                asset.is_returned = False
                asset.save()
                
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {index+2}: {str(e)}")
                error_count += 1
    
    message = f"Processed {success_count} allocations successfully."
    if error_count > 0:
        message += f" {error_count} errors occurred."
        if errors:
            message += " First error: " + errors[0]
    
    return {'message': message, 'success_count': success_count, 'error_count': error_count, 'errors': errors}


@login_required
def download_template(request, template_type):
    """Download CSV template for mass upload"""
    if template_type == 'asset':
        # Create asset template
        columns = [
            'serial_number', 'name', 'model', 'type', 'company', 
            'purchase_date', 'purchase_price', 'imei_number', 'processor', 
            'ram', 'ssd_capacity', 'hdd_capacity', 'os', 'os_licence', 
            'office', 'office_licence', 'specs', 'accessories', 'ip',
            'applications_description'
        ]
        filename = 'asset_upload_template.csv'
        
    elif template_type == 'employee':
        # Create employee template
        columns = [
            'first_name', 'last_name', 'email', 'department', 
            'phone_number', 'company'
        ]
        filename = 'employee_upload_template.csv'
        
    elif template_type == 'allocation':
        # Create allocation template
        columns = [
            'asset_serial_number', 'employee_email', 'allocation_date',
            'return_date', 'asset_status'
        ]
        filename = 'allocation_upload_template.csv'
        
    else:
        return HttpResponse("Invalid template type", status=400)
    
    # Create empty DataFrame with required columns
    df = pd.DataFrame(columns=columns)
    
    # Create response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Write DataFrame to response
    df.to_csv(response, index=False)
    
    return response



class AssetReportView(LoginRequiredMixin, View):
    def get(self, request, report_type):
        # Get the requested format (default to Excel)
        format = request.GET.get('format', 'excel')
        
        if report_type == 'total_assets':
            return self.total_assets_report(request, format)
        elif report_type == 'allocated_assets':
            return self.allocated_assets_report(request, format)
        elif report_type == 'unallocated_assets':
            return self.unallocated_assets_report(request, format)
        elif report_type == 'by_status':
            return self.assets_by_status_report(request, format)
        elif report_type == 'by_department':
            return self.assets_by_department_report(request, format)
        else:
            return HttpResponse("Invalid report type", status=400)
    
    def total_assets_report(self, request, format):
        """Generate report of all assets"""
        assets = Asset.objects.select_related('company').order_by('name', 'serial_number')
        
        data = []
        for asset in assets:
            current_allocation = asset.current_allocation()
            allocated_to = f"{current_allocation.employee_allocated.first_name} {current_allocation.employee_allocated.last_name}" if current_allocation else "Not Allocated"
            department = current_allocation.employee_allocated.department if current_allocation else "N/A"
            
            data.append({
                'Name': asset.name,
                'Serial Number': asset.serial_number,
                'Type': asset.get_type_display(),
                'Model': asset.model,
                'Company': asset.company.name,
                'Status': 'Allocated' if asset.is_allocated else 'Unallocated',
                'Allocated To': allocated_to,
                'Department': department,
                'Purchase Date': asset.purchase_date.strftime("%Y-%m-%d") if asset.purchase_date else "",
                'Purchase Price': str(asset.purchase_price) if asset.purchase_price else ""
            })
        
        return self.export_to_excel(data, "Total Assets Report")
    
    def allocated_assets_report(self, request, format):
        """Generate report of allocated assets"""
        assets = Asset.objects.filter(is_allocated=True).select_related('company').order_by('name', 'serial_number')
        
        data = []
        for asset in assets:
            current_allocation = asset.current_allocation()
            if current_allocation:
                data.append({
                    'Name': asset.name,
                    'Serial Number': asset.serial_number,
                    'Type': asset.get_type_display(),
                    'Model': asset.model,
                    'Company': asset.company.name,
                    'Allocated To': f"{current_allocation.employee_allocated.first_name} {current_allocation.employee_allocated.last_name}",
                    'Department': current_allocation.employee_allocated.department,
                    'Allocation Date': current_allocation.allocation_date.strftime("%Y-%m-%d"),
                    'Asset Status': current_allocation.get_asset_status_display(),
                    'Purchase Date': asset.purchase_date.strftime("%Y-%m-%d") if asset.purchase_date else "",
                })
        
        return self.export_to_excel(data, "Allocated Assets Report")
    
    def unallocated_assets_report(self, request, format):
        """Generate report of unallocated assets"""
        assets = Asset.objects.filter(is_allocated=False).select_related('company').order_by('name', 'serial_number')
        
        data = []
        for asset in assets:
            data.append({
                'Name': asset.name,
                'Serial Number': asset.serial_number,
                'Type': asset.get_type_display(),
                'Model': asset.model,
                'Company': asset.company.name,
                'Purchase Date': asset.purchase_date.strftime("%Y-%m-%d") if asset.purchase_date else "",
                'Purchase Price': str(asset.purchase_price) if asset.purchase_price else "",
                'Status': 'Available' if not asset.is_returned else 'Returned'
            })
        
        return self.export_to_excel(data, "Unallocated Assets Report")
    
    def assets_by_status_report(self, request, format):
        """Generate report grouping assets by status"""
        # Get status filter from request if provided
        status_filter = request.GET.get('status', None)
        
        if status_filter:
            allocations = AssetAllocation.objects.filter(asset_status=status_filter)
        else:
            allocations = AssetAllocation.objects.all()
        
        # Group by status
        allocations = allocations.select_related('asset', 'employee_allocated').order_by('asset_status')
        
        data = []
        for allocation in allocations:
            data.append({
                'Asset Name': allocation.asset.name,
                'Serial Number': allocation.asset.serial_number,
                'Type': allocation.asset.get_type_display(),
                'Status': allocation.get_asset_status_display(),
                'Allocated To': f"{allocation.employee_allocated.first_name} {allocation.employee_allocated.last_name}",
                'Department': allocation.employee_allocated.department,
                'Allocation Date': allocation.allocation_date.strftime("%Y-%m-%d"),
                'Return Date': allocation.return_date.strftime("%Y-%m-%d") if allocation.return_date else "Not Returned"
            })
        
        report_title = "Assets by Status Report"
        if status_filter:
            report_title += f" - {dict(AssetAllocation.ASSET_STATUS_CHOICES).get(status_filter, status_filter)}"
        
        return self.export_to_excel(data, report_title)
    
    def assets_by_department_report(self, request, format):
        """Generate report grouping assets by department"""
        # Get department filter from request if provided
        department_filter = request.GET.get('department', None)
        
        # Get allocations with related data
        allocations = AssetAllocation.objects.filter(
            return_date__isnull=True  # Only current allocations
        ).select_related(
            'employee_allocated', 'asset'
        )
        
        if department_filter:
            allocations = allocations.filter(employee_allocated__department=department_filter)
        
        # Group by department
        allocations = allocations.order_by('employee_allocated__department')
        
        data = []
        for allocation in allocations:
            data.append({
                'Department': allocation.employee_allocated.department,
                'Asset Name': allocation.asset.name,
                'Serial Number': allocation.asset.serial_number,
                'Type': allocation.asset.get_type_display(),
                'Allocated To': f"{allocation.employee_allocated.first_name} {allocation.employee_allocated.last_name}",
                'Email': allocation.employee_allocated.email,
                'Allocation Date': allocation.allocation_date.strftime("%Y-%m-%d"),
                'Asset Status': allocation.get_asset_status_display()
            })
        
        report_title = "Assets by Department Report"
        if department_filter:
            report_title += f" - {department_filter}"
        
        return self.export_to_excel(data, report_title)
    
    def export_to_excel(self, data, title):
        """Export data to Excel format"""
        if not data:
            # Return empty Excel file with message
            df = pd.DataFrame({"Message": ["No data available for this report"]})
        else:
            df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=title[:30], index=False)  # Sheet name max 31 chars
            
            # Auto-adjust columns width
            worksheet = writer.sheets[title[:30]]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Prepare HTTP response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f"{title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Write Excel file to response
        output.seek(0)
        response.write(output.getvalue())
        
        return response
    
@login_required
def reports_dashboard(request):
    """Display all available reports"""
    # Get counts for dashboard
    total_assets = Asset.objects.count()
    allocated_assets = Asset.objects.filter(is_allocated=True).count()
    unallocated_assets = total_assets - allocated_assets
    
    # Get unique departments
    departments = Employee.objects.values_list('department', flat=True).distinct()
    
    context = {
        'total_assets': total_assets,
        'allocated_assets': allocated_assets,
        'unallocated_assets': unallocated_assets,
        'departments': departments,
        'status_choices': AssetAllocation.ASSET_STATUS_CHOICES,
    }
    return render(request, 'asset/reports_dashboard.html', context)

