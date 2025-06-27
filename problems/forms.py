from django import forms
from .models import Submission, ProblemDiscussion


class SubmissionForm(forms.ModelForm):
    """Form for code submissions."""
    
    class Meta:
        model = Submission
        fields = ['code', 'language']
        widgets = {
            'code': forms.Textarea(attrs={
                'class': 'font-mono text-sm',
                'rows': 20,
                'placeholder': 'Write your code here...'
            }),
            'language': forms.Select(attrs={
                'class': 'form-select'
            })
        }


class DiscussionForm(forms.ModelForm):
    """Form for problem discussions."""
    
    class Meta:
        model = ProblemDiscussion
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Share your thoughts or ask a question...'
            })
        } 