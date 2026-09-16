 
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Service, ServiceCategory
from .forms import ServiceForm, ServiceSearchForm
from accounts.models import ProviderProfile


def service_list(request):
    """
    Public page showing all available services.
    Supports search and filtering.
    """

    services = Service.objects.filter(
        is_available=True
    ).select_related(
        'provider__user',
        'category'
    )

    form = ServiceSearchForm(request.GET)

    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        city = form.cleaned_data.get('city')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')

        if query:
            services = services.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(provider__user__first_name__icontains=query)
            )

        if category:
            services = services.filter(category=category)

        if city:
            services = services.filter(
                provider__city__icontains=city
            )

        if min_price:
            services = services.filter(price__gte=min_price)

        if max_price:
            services = services.filter(price__lte=max_price)

    categories = ServiceCategory.objects.filter(is_active=True)

    context = {
        'services': services,
        'form': form,
        'categories': categories,
        'total_results': services.count(),
    }
    return render(request, 'services/service_list.html', context)


def service_detail(request, pk):
    """
    Detail page for a single service.
    Shows provider info, price, reviews.
    """

    service = get_object_or_404(Service, pk=pk, is_available=True)
    provider = service.provider

    # Get other services by same provider
    other_services = Service.objects.filter(
        provider=provider,
        is_available=True
    ).exclude(pk=pk)[:3]

    context = {
        'service': service,
        'provider': provider,
        'other_services': other_services,
    }
    return render(request, 'services/service_detail.html', context)


def category_services(request, pk):
    """
    Show all services in a specific category.
    """

    category = get_object_or_404(ServiceCategory, pk=pk, is_active=True)
    services = Service.objects.filter(
        category=category,
        is_available=True
    ).select_related('provider__user')

    context = {
        'category': category,
        'services': services,
    }
    return render(request, 'services/category_services.html', context)


def provider_public_profile(request, pk):
    """
    Public profile page for a service provider.
    """

    provider = get_object_or_404(ProviderProfile, pk=pk)
    services = Service.objects.filter(
        provider=provider,
        is_available=True
    )

    context = {
        'provider': provider,
        'services': services,
    }
    return render(request, 'services/provider_profile.html', context)


# --- Provider Only Views ---

@login_required(login_url='/accounts/login/')
def my_services(request):
    """
    Provider sees and manages their own services.
    """

    if not request.user.is_provider():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    provider = get_object_or_404(ProviderProfile, user=request.user)
    services = Service.objects.filter(provider=provider)

    context = {
        'services': services,
        'provider': provider,
    }
    return render(request, 'services/my_services.html', context)


@login_required(login_url='/accounts/login/')
def add_service(request):
    """
    Provider adds a new service.
    """

    if not request.user.is_provider():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    provider = get_object_or_404(ProviderProfile, user=request.user)

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.provider = provider
            service.save()
            messages.success(request, 'Service added successfully!')
            return redirect('my_services')
    else:
        form = ServiceForm()

    return render(request, 'services/add_service.html', {'form': form})


@login_required(login_url='/accounts/login/')
def edit_service(request, pk):
    """
    Provider edits an existing service.
    """

    if not request.user.is_provider():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    provider = get_object_or_404(ProviderProfile, user=request.user)
    service = get_object_or_404(Service, pk=pk, provider=provider)

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully!')
            return redirect('my_services')
    else:
        form = ServiceForm(instance=service)

    return render(request, 'services/edit_service.html', {
        'form': form,
        'service': service
    })


@login_required(login_url='/accounts/login/')
def delete_service(request, pk):
    """
    Provider deletes a service.
    """

    if not request.user.is_provider():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    provider = get_object_or_404(ProviderProfile, user=request.user)
    service = get_object_or_404(Service, pk=pk, provider=provider)

    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service deleted successfully.')
        return redirect('my_services')

    return render(request, 'services/delete_service.html', {
        'service': service
    })