from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ResumeScanForm
from .models import ResumeScan
from django.contrib import messages
from .analyzer import ResumeAnalyzer
import logging

logger = logging.getLogger(__name__)


@login_required
def upload_resume(request):
    """Upload and analyze resume."""
    if request.method == 'POST':
        form = ResumeScanForm(request.POST, request.FILES)
        if form.is_valid():
            scan = form.save(commit=False)
            scan.user = request.user
            
            # Analyze resume using advanced analyzer
            try:
                analyzer = ResumeAnalyzer(
                    scan.resume_file,
                    scan.job_field,
                    scan.job_description
                )
                results = analyzer.analyze()
                
                # Save results
                scan.ats_score = results.get('ats_score', 0)
                scan.keyword_score = results.get('keyword_score', 0)
                scan.suggestions = results.get('suggestions', [])
                scan.report = analyzer.generate_report()
                
                # Store detailed results in JSON for display
                scan.analysis_data = {
                    'format_score': results.get('format_score', 0),
                    'content_score': results.get('content_score', 0),
                    'overall_score': results.get('overall_score', 0),
                    'strengths': results.get('strengths', []),
                    'weaknesses': results.get('weaknesses', []),
                    'keywords': results.get('keywords', {}),
                    'sections': results.get('sections', {}),
                    'contact_info': results.get('contact_info', {}),
                    'format_issues': results.get('format_issues', []),
                    'word_count': results.get('word_count', 0),
                }
                
                scan.save()
                messages.success(request, '🎉 Resume analyzed successfully!')
                return redirect('resume_scanner:scan_result', scan_id=scan.id)
                
            except Exception as e:
                logger.error(f"Resume analysis failed: {e}")
                messages.error(request, f'Analysis failed: {str(e)}')
    else:
        form = ResumeScanForm()
    
    # Get user's previous scans
    previous_scans = ResumeScan.objects.filter(user=request.user).order_by('-uploaded_at')[:5]
    
    return render(request, 'resume_scanner/upload_resume.html', {
        'form': form,
        'previous_scans': previous_scans
    })


@login_required
def scan_result(request, scan_id):
    """Display detailed resume analysis results."""
    scan = get_object_or_404(ResumeScan, id=scan_id, user=request.user)
    
    # Get analysis data
    analysis_data = getattr(scan, 'analysis_data', {})
    
    context = {
        'scan': scan,
        'analysis_data': analysis_data,
        'format_score': analysis_data.get('format_score', 0),
        'content_score': analysis_data.get('content_score', 0),
        'overall_score': analysis_data.get('overall_score', 0),
        'strengths': analysis_data.get('strengths', []),
        'weaknesses': analysis_data.get('weaknesses', []),
        'keywords': analysis_data.get('keywords', {}),
        'sections': analysis_data.get('sections', {}),
        'contact_info': analysis_data.get('contact_info', {}),
    }
    
    return render(request, 'resume_scanner/scan_result.html', context)


@login_required
def scan_history(request):
    """View all resume scans."""
    scans = ResumeScan.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'resume_scanner/scan_history.html', {'scans': scans})
