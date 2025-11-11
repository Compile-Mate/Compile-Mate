from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from .models import Certification, UserCertification
from learning_paths.models import LearningPath, PathEnrollment
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph


def certificate_list(request):
    """View for listing all available certifications."""
    certifications = Certification.objects.filter(is_active=True).order_by('difficulty_level', 'name')
    
    # Get user's earned certificates if authenticated
    user_certificates = []
    if request.user.is_authenticated:
        user_certificates = UserCertification.objects.filter(
            user=request.user
        ).select_related('certification').order_by('-earned_at')
    
    context = {
        'certifications': certifications,
        'user_certificates': user_certificates,
    }
    return render(request, 'certifications/certificate_list.html', context)


def certificate_detail(request, slug):
    """View for certification details."""
    certification = get_object_or_404(Certification, slug=slug, is_active=True)
    
    # Check if user has earned this certificate
    user_certificate = None
    progress = None
    if request.user.is_authenticated:
        try:
            user_certificate = UserCertification.objects.get(
                user=request.user,
                certification=certification
            )
        except UserCertification.DoesNotExist:
            pass
        
        # Calculate progress if linked to learning path
        if certification.learning_path:
            try:
                enrollment = PathEnrollment.objects.get(
                    user=request.user,
                    learning_path=certification.learning_path
                )
                progress = enrollment.progress_percentage
            except PathEnrollment.DoesNotExist:
                progress = 0
    
    context = {
        'certification': certification,
        'user_certificate': user_certificate,
        'progress': progress,
    }
    return render(request, 'certifications/certificate_detail.html', context)


@login_required
def my_certificates(request):
    """View for user's earned certificates."""
    user_certificates = UserCertification.objects.filter(
        user=request.user
    ).select_related('certification').order_by('-earned_at')
    
    context = {
        'user_certificates': user_certificates,
    }
    return render(request, 'certifications/my_certificates.html', context)


@login_required
def download_certificate(request, certificate_id):
    """Generate and download PDF certificate."""
    user_cert = get_object_or_404(
        UserCertification,
        id=certificate_id,
        user=request.user
    )
    
    # Create PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)
    
    # Background
    p.setFillColor(colors.HexColor('#f0f9ff'))
    p.rect(0, 0, width, height, fill=True, stroke=False)
    
    # Border
    p.setStrokeColor(colors.HexColor('#2563eb'))
    p.setLineWidth(4)
    p.rect(0.5*inch, 0.5*inch, width-inch, height-inch, fill=False, stroke=True)
    
    # Title
    p.setFillColor(colors.HexColor('#1e40af'))
    p.setFont("Helvetica-Bold", 36)
    p.drawCentredString(width/2, height-1.5*inch, "CERTIFICATE OF COMPLETION")
    
    # CompileMate logo text
    p.setFillColor(colors.HexColor('#4f46e5'))
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width/2, height-2*inch, "CompileMate")
    
    # Body text
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 18)
    p.drawCentredString(width/2, height-3*inch, "This certifies that")
    
    # User name
    p.setFont("Helvetica-Bold", 32)
    p.setFillColor(colors.HexColor('#1e40af'))
    p.drawCentredString(width/2, height-3.7*inch, request.user.username)
    
    # Achievement text
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 18)
    p.drawCentredString(width/2, height-4.4*inch, "has successfully completed")
    
    # Certification name
    p.setFont("Helvetica-Bold", 28)
    p.setFillColor(colors.HexColor('#2563eb'))
    p.drawCentredString(width/2, height-5.2*inch, user_cert.certification.name)
    
    # Date
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 14)
    date_text = f"Completed on {user_cert.earned_at.strftime('%B %d, %Y')}"
    p.drawCentredString(width/2, height-6*inch, date_text)
    
    # Certificate ID
    p.setFont("Helvetica", 10)
    p.drawCentredString(width/2, 1.2*inch, f"Certificate ID: {user_cert.certificate_id}")
    
    # Verification URL
    p.setFillColor(colors.HexColor('#4f46e5'))
    verify_url = f"compilemate.com/certificates/verify/{user_cert.certificate_id}"
    p.drawCentredString(width/2, 0.9*inch, f"Verify at: {verify_url}")
    
    # Signature line
    p.setStrokeColor(colors.black)
    p.setLineWidth(1)
    p.line(width/2 - 2*inch, 2*inch, width/2 + 2*inch, 2*inch)
    p.setFont("Helvetica", 12)
    p.drawCentredString(width/2, 1.7*inch, "CompileMate Team")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="CompileMate_{user_cert.certification.slug}_certificate.pdf"'
    
    return response


def verify_certificate(request, certificate_id):
    """Public certificate verification page."""
    try:
        user_cert = UserCertification.objects.select_related(
            'user', 'certification'
        ).get(certificate_id=certificate_id)
        
        context = {
            'user_certificate': user_cert,
            'verified': True,
        }
    except UserCertification.DoesNotExist:
        context = {
            'verified': False,
        }
    
    return render(request, 'certifications/verify_certificate.html', context)
