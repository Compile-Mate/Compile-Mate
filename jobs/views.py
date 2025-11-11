from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import JobPosting, JobApplication, Company


def job_list(request):
    """View for listing all active job postings."""
    jobs = JobPosting.objects.filter(
        status='active',
        expires_at__gte=timezone.now()
    ).select_related('company').prefetch_related('challenge_problems')
    
    # Filters
    job_type = request.GET.get('job_type')
    experience = request.GET.get('experience')
    remote = request.GET.get('remote')
    search = request.GET.get('search')
    
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if experience:
        jobs = jobs.filter(experience_level=experience)
    if remote:
        jobs = jobs.filter(remote_ok=True)
    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(company__name__icontains=search)
        )
    
    context = {
        'jobs': jobs,
        'job_types': JobPosting.JOB_TYPE_CHOICES,
        'experience_levels': JobPosting.EXPERIENCE_CHOICES,
    }
    return render(request, 'jobs/job_list.html', context)


def job_detail(request, slug):
    """View for job posting details."""
    job = get_object_or_404(
        JobPosting.objects.select_related('company').prefetch_related('challenge_problems'),
        slug=slug,
        status='active'
    )
    
    # Check if user has already applied
    has_applied = False
    user_application = None
    if request.user.is_authenticated:
        try:
            user_application = JobApplication.objects.get(job=job, applicant=request.user)
            has_applied = True
        except JobApplication.DoesNotExist:
            pass
    
    context = {
        'job': job,
        'has_applied': has_applied,
        'user_application': user_application,
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required
def apply_job(request, slug):
    """View for applying to a job."""
    job = get_object_or_404(JobPosting, slug=slug, status='active')
    
    # Check if already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied to this job!')
        return redirect('jobs:job_detail', slug=slug)
    
    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter', '')
        portfolio_url = request.POST.get('portfolio_url', '')
        
        # Create application
        application = JobApplication.objects.create(
            job=job,
            applicant=request.user,
            cover_letter=cover_letter,
            portfolio_url=portfolio_url,
            status='applied'
        )
        
        # Update job applications count
        job.applications_count += 1
        job.save()
        
        messages.success(request, f'Successfully applied to {job.title}!')
        return redirect('jobs:my_applications')
    
    context = {
        'job': job,
    }
    return render(request, 'jobs/apply_job.html', context)


@login_required
def my_applications(request):
    """View for user's job applications."""
    applications = JobApplication.objects.filter(
        applicant=request.user
    ).select_related('job', 'job__company').order_by('-applied_at')
    
    context = {
        'applications': applications,
    }
    return render(request, 'jobs/my_applications.html', context)


@login_required
def withdraw_application(request, application_id):
    """View for withdrawing a job application."""
    application = get_object_or_404(
        JobApplication,
        id=application_id,
        applicant=request.user
    )
    
    if application.status in ['applied', 'under_review', 'challenge_sent']:
        application.status = 'withdrawn'
        application.save()
        
        # Update job applications count
        application.job.applications_count -= 1
        application.job.save()
        
        messages.success(request, 'Application withdrawn successfully.')
    else:
        messages.error(request, 'Cannot withdraw application at this stage.')
    
    return redirect('jobs:my_applications')


def companies_list(request):
    """View for listing all verified companies."""
    companies = Company.objects.filter(is_verified=True).order_by('name')
    
    search = request.GET.get('search')
    if search:
        companies = companies.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    context = {
        'companies': companies,
    }
    return render(request, 'jobs/companies_list.html', context)


def company_detail(request, slug):
    """View for company details and their job postings."""
    company = get_object_or_404(Company, slug=slug, is_verified=True)
    
    jobs = JobPosting.objects.filter(
        company=company,
        status='active',
        expires_at__gte=timezone.now()
    ).order_by('-posted_at')
    
    context = {
        'company': company,
        'jobs': jobs,
    }
    return render(request, 'jobs/company_detail.html', context)
