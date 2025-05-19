from django.urls import path
from .views import PackageCreateView, PackageListView, PackageUpdateView, export_packages_csv

urlpatterns = [
    path('packages/', PackageListView.as_view(), name='package_list'),
    path('packages/new/', PackageCreateView.as_view(), name='package_create'),
    path('packages/report/', export_packages_csv, name='package_create'),
    path('packages/<int:pk>/edit/', PackageUpdateView.as_view(), name='package_edit'),
]