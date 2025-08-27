# urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('assign_asset/', views.assign_asset, name='assign_asset'),
    path('return_asset/', views.return_asset, name='return_asset'),
    path('asset/<int:asset_id>/return/', views.return_asset, name='return_asset'),    
    path('success/', views.success_page, name='success_page'),
    path('add_employee/', views.add_employee, name='add_employee'),
    path('add_asset/', views.add_asset, name='add_asset'),
    path('assets/', views.asset_list, name='asset_list'),
    path('asset-allocation/', views.asset_allocation_form, name='asset_allocation_form'),
    path('asset-return/', views.asset_return_form, name='asset_return_form'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('password_change/', views.password_change_view, name='password_change'),
    path('password_reset/', views.password_reset_view, name='password_reset'),
    path('password_reset_done/', views.password_reset_done_view, name='password_reset_done'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('asset_disposal', views.asset_disposal, name='asset_disposal'),
    path('asset_detail/<int:asset_id>/', views.asset_detail, name='asset_detail'),
    path('assetreturn_detail/<int:asset_id>/', views.assetreturn_detail, name='assetreturn_detail'),
    path('signin/',views.signin, name='signin'),
    path('signup/',views.signup, name='signup'),
    path('profile/',views.profile, name='profile'),
    path('search/', views.search, name='search'),
    path('asset/<int:asset_id>/', views.asset_detail, name='asset_detail'),
    path('employee/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('reports/all-assets/', views.AllAssetsReport.as_view(), name='all_assets_report'),
    path('reports/allocated-assets/', views.AllocatedAssetsReport.as_view(), name='allocated_assets_report'),
    path('reports/unallocated-assets/', views.UnallocatedAssetsReport.as_view(), name='unallocated_assets_report'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('export-assets/', views.export_assets, name='export_assets'),
    path('reports/asset-type/<str:type>/', views.AssetTypeReportView.as_view(), name='asset_type_report'),
    path('assets/import/', views.import_assets, name='import_assets'),
    path('users/import/', views.import_users, name='import_users'),
    path('mass-upload/', views.mass_upload, name='mass_upload'),
    path('download-template/<str:template_type>/', views.download_template, name='download_template'),
    path('allocation/<int:allocation_id>/form/', views.generate_allocation_form, name='generate_allocation_form'),
    path('reports/<str:report_type>/', views.AssetReportView.as_view(), name='asset_report'),
    path('report/', views.reports_dashboard, name='reports_dashboard')
    # Add these to your urlpatterns

]


