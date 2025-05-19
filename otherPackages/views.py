from django.views.generic import CreateView, ListView
from .models import OtherPackage
from .forms import OtherPackageForm
import csv
from django.http import HttpResponse
from django.views.generic import UpdateView


class PackageCreateView(CreateView):
    model = OtherPackage
    form_class = OtherPackageForm
    template_name = 'package_form.html'
    success_url = '/others/packages/'

    def get_form_kwargs(self):
        """Remove 'created_by' from the form kwargs"""
        kwargs = super().get_form_kwargs()
        kwargs.pop('created_by', None)  # Remove if present
        return kwargs

    def form_valid(self, form):
        """Set the created_by field to current user before saving"""
        if form.is_valid():
            form.instance.created_by = self.request.user
            self.object = form.save()
        return super().form_valid(form)
    

class PackageListView(ListView):
    model = OtherPackage
    template_name = 'package_list.html'
    context_object_name = 'packages'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs
    
    

class PackageUpdateView(UpdateView):
    model = OtherPackage
    form_class = OtherPackageForm
    template_name = 'package_form.html'
    success_url = '/packages/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop('created_by', None)
        return kwargs

    def form_valid(self, form):
        # Add any additional logic before saving
        return super().form_valid(form)
    
    
def export_packages_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="service_packages.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Client Name', 'Service Type', 'Start Time', 'End Time', 
        'Duration (hrs)', 'Total Amount', 'Status', 'Created By'
    ])

    packages = OtherPackage.objects.select_related('created_by').all()
    
    for pkg in packages:
        writer.writerow([
            pkg.client_name,
            pkg.get_service_type_display(),
            pkg.start_time.strftime("%Y-%m-%d %H:%M"),
            pkg.end_time.strftime("%Y-%m-%d %H:%M"),
            pkg.duration,
            pkg.total_amount,
            pkg.status,
            pkg.created_by.username if pkg.created_by else 'System'
        ])

    return response