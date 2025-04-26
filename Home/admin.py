from django.contrib import admin
from Home.models import User, Problem, Submission, TestCases, ProblemSolution, Activity
from django.forms import ModelForm
from django.utils import timezone
from django import forms

class TestCasesInline(admin.TabularInline):
    model = TestCases
    extra = 2
    fields = ('input', 'output')
    fk_name = 'problem'

class ProblemSolutionInline(admin.StackedInline):
    model = ProblemSolution
    max_num = 1
    can_delete = False
    fieldsets = (
        ('Function Information', {
            'fields': ('function_name',)
        }),
        ('Python', {
            'fields': ('python_solution', 'python_template'),
        }),
        ('C++', {
            'fields': ('cpp_solution', 'cpp_template'),
        }),
        ('Java', {
            'fields': ('java_solution', 'java_template'),
        }),
    )

class ProblemAdminForm(forms.ModelForm):
    constraints = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 5,
            'placeholder': '2 <= nums.length <= 104\n-109 <= nums[i] <= 109\nExactly one solution exists.'
        }),
        help_text="Enter each constraint on a new line",
        required=False
    )

    class Meta:
        model = Problem
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        constraints = cleaned_data.get('constraints')
        
        if constraints:
            # Split by newlines and filter out empty lines
            constraints_list = [c.strip() for c in constraints.split('\n') if c.strip()]
            cleaned_data['constraints'] = '\n'.join(constraints_list)
        
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.constraints:
            if isinstance(self.instance.constraints, list):
                self.initial['constraints'] = '\n'.join(self.instance.constraints)
            elif isinstance(self.instance.constraints, str):
                try:
                    # If it's a JSON string, parse it and convert to text
                    import json
                    constraints_list = json.loads(self.instance.constraints)
                    if isinstance(constraints_list, list):
                        self.initial['constraints'] = '\n'.join(constraints_list)
                except json.JSONDecodeError:
                    # If it's already a text string, use it as is
                    self.initial['constraints'] = self.instance.constraints

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    form = ProblemAdminForm
    list_display = ('id', 'name', 'type', 'difficuilty')
    list_filter = ('type', 'difficuilty')
    search_fields = ('name', 'statement')
    inlines = [ProblemSolutionInline, TestCasesInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'type', 'difficuilty')
        }),
        ('Problem Description', {
            'fields': ('statement', 'task', 'constraints')
        }),
        ('Complexity', {
            'fields': ('time_complexity', 'space_complexity'),
            'classes': ('collapse',)
        }),
    )

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'email', 'problems_solved')
    search_fields = ('username', 'name', 'email')
    readonly_fields = ('problems_solved',)

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'verdict', 'time')
    list_filter = ('verdict', 'time')
    search_fields = ('user__username', 'problem__name')
    exclude = ('time',)  # Hide time field from form
    
    def save_model(self, request, obj, form, change):
        if not obj.time:  # Only set time if it's not already set
            obj.time = timezone.now()
        
        # First save the submission
        super().save_model(request, obj, form, change)
        
        # Update user's solved problems count if verdict indicates success
        if obj.verdict in ["Accepted", "Passed"]:
            # Only increment if this is the first successful solution for this problem
            if not Submission.objects.filter(
                user=obj.user,
                problem=obj.problem,
                verdict__in=["Accepted", "Passed"]
            ).exclude(id=obj.id).exists():  # Exclude current submission from check
                obj.user.problems_solved += 1
                obj.user.save()

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'title', 'time')
    list_filter = ('type', 'time')
    search_fields = ('user__username', 'title', 'description')
    readonly_fields = ('time',)

# We don't need to register TestCases separately as it's managed through Problem
# We don't need to register ProblemSolution separately as it's managed through Problem