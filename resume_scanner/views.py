from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ResumeScanForm
from .models import ResumeScan
from django.contrib import messages
import os

# Create your views here.

@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeScanForm(request.POST, request.FILES)
        if form.is_valid():
            scan = form.save(commit=False)
            scan.user = request.user
            scan.ats_score, scan.keyword_score, scan.suggestions, scan.report = analyze_resume(scan.resume_file, scan.job_field, scan.job_description)
            scan.save()
            messages.success(request, 'Resume uploaded and analyzed successfully!')
            return redirect('resume_scanner:scan_result', scan_id=scan.id)
    else:
        form = ResumeScanForm()
    return render(request, 'resume_scanner/upload_resume.html', {'form': form})

@login_required
def scan_result(request, scan_id):
    scan = get_object_or_404(ResumeScan, id=scan_id, user=request.user)
    return render(request, 'resume_scanner/scan_result.html', {'scan': scan})

# --- Placeholder logic for ATS/keyword scoring and suggestions ---
def analyze_resume(resume_file, job_field, job_description):
    # In production, use NLP, PDF/DOCX parsing, and AI/ML here
    # For now, use dummy logic
    ats_score = 70.0  # Placeholder
    keyword_score = 60.0  # Placeholder
    suggestions = [
        'Add a professional summary at the top of your resume.',
        'Include more relevant keywords from the job description.',
        'Use standard section headings: Education, Experience, Skills.',
        'Avoid using tables or images that confuse ATS systems.',
        'Quantify your achievements with numbers where possible.'
    ]
    report = f"This is a placeholder report. Your resume ATS score is {ats_score}.\nKeyword match score: {keyword_score}.\nAdd more keywords from the job description for a better match."
    return ats_score, keyword_score, suggestions, report
