from django import forms
from .models import ResumeScan

class ResumeScanForm(forms.ModelForm):
    class Meta:
        model = ResumeScan
        fields = ['resume_file', 'job_field', 'job_description']
        widgets = {
            'job_description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Paste the job description here (optional)'}),
            'job_field': forms.TextInput(attrs={'placeholder': 'e.g. Software Engineer, Data Scientist'}),
        } 