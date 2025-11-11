"""
Advanced ATS Resume Analyzer for CompileMate
Analyzes resumes against job descriptions with AI-powered insights.
"""

import re
import PyPDF2
import docx
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class ResumeAnalyzer:
    """Comprehensive resume analysis engine."""
    
    # ATS-friendly keywords by category
    TECHNICAL_SKILLS_KEYWORDS = {
        'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'rust', 'php', 'swift', 'kotlin'],
        'web': ['html', 'css', 'react', 'angular', 'vue', 'nodejs', 'django', 'flask', 'spring', 'express'],
        'data': ['sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'pandas', 'numpy', 'spark'],
        'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd'],
        'ml_ai': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'nlp', 'computer vision'],
    }
    
    SOFT_SKILLS_KEYWORDS = [
        'leadership', 'communication', 'teamwork', 'problem-solving', 'analytical',
        'collaborative', 'agile', 'scrum', 'management', 'mentoring'
    ]
    
    REQUIRED_SECTIONS = ['experience', 'education', 'skills']
    OPTIONAL_SECTIONS = ['summary', 'projects', 'certifications', 'achievements', 'awards']
    
    def __init__(self, resume_file, job_field='', job_description=''):
        self.resume_file = resume_file
        self.job_field = job_field.lower()
        self.job_description = job_description.lower()
        self.resume_text = ''
        self.analysis_results = {}
    
    def analyze(self):
        """Main analysis entry point."""
        try:
            # Extract text from resume
            self.resume_text = self._extract_text()
            
            if not self.resume_text:
                return self._error_result("Could not extract text from resume")
            
            # Perform analysis
            self.analysis_results = {
                'ats_score': 0,
                'keyword_score': 0,
                'format_score': 0,
                'content_score': 0,
                'overall_score': 0,
                'sections': self._analyze_sections(),
                'keywords': self._analyze_keywords(),
                'format_issues': self._check_format(),
                'contact_info': self._extract_contact_info(),
                'suggestions': [],
                'strengths': [],
                'weaknesses': [],
                'missing_keywords': [],
                'word_count': len(self.resume_text.split()),
            }
            
            # Calculate scores
            self._calculate_scores()
            
            # Generate suggestions
            self._generate_suggestions()
            
            return self.analysis_results
            
        except Exception as e:
            logger.error(f"Resume analysis error: {e}")
            return self._error_result(f"Analysis failed: {str(e)}")
    
    def _extract_text(self):
        """Extract text from PDF or DOCX file."""
        file_extension = self.resume_file.name.split('.')[-1].lower()
        
        try:
            if file_extension == 'pdf':
                return self._extract_from_pdf()
            elif file_extension in ['docx', 'doc']:
                return self._extract_from_docx()
            else:
                return ''
        except Exception as e:
            logger.error(f"Text extraction error: {e}")
            return ''
    
    def _extract_from_pdf(self):
        """Extract text from PDF file."""
        text = ''
        try:
            pdf_reader = PyPDF2.PdfReader(self.resume_file)
            for page in pdf_reader.pages:
                text += page.extract_text() + '\n'
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
        return text.lower()
    
    def _extract_from_docx(self):
        """Extract text from DOCX file."""
        text = ''
        try:
            doc = docx.Document(self.resume_file)
            for paragraph in doc.paragraphs:
                text += paragraph.text + '\n'
        except Exception as e:
            logger.error(f"DOCX extraction error: {e}")
        return text.lower()
    
    def _analyze_sections(self):
        """Analyze resume sections."""
        sections_found = {}
        
        # Check for required sections
        for section in self.REQUIRED_SECTIONS:
            sections_found[section] = section in self.resume_text or \
                                     any(keyword in self.resume_text for keyword in [
                                         'work experience', 'professional experience',
                                         'education', 'academic', 'skills', 'technical skills'
                                     ])
        
        # Check for optional sections
        for section in self.OPTIONAL_SECTIONS:
            sections_found[section] = section in self.resume_text or \
                                     any(keyword in self.resume_text for keyword in [
                                         'summary', 'objective', 'profile',
                                         'projects', 'portfolio',
                                         'certifications', 'certificates',
                                         'achievements', 'accomplishments', 'awards'
                                     ])
        
        return sections_found
    
    def _analyze_keywords(self):
        """Analyze keywords against job description."""
        keywords_analysis = {
            'technical_skills': [],
            'soft_skills': [],
            'job_description_match': [],
            'total_keywords_found': 0
        }
        
        # Check technical skills
        for category, keywords in self.TECHNICAL_SKILLS_KEYWORDS.items():
            found = [kw for kw in keywords if kw in self.resume_text]
            keywords_analysis['technical_skills'].extend(found)
        
        # Check soft skills
        found_soft = [skill for skill in self.SOFT_SKILLS_KEYWORDS if skill in self.resume_text]
        keywords_analysis['soft_skills'] = found_soft
        
        # Match against job description
        if self.job_description:
            jd_words = set(re.findall(r'\b\w{4,}\b', self.job_description))  # Words with 4+ chars
            resume_words = set(re.findall(r'\b\w{4,}\b', self.resume_text))
            matched = jd_words & resume_words
            keywords_analysis['job_description_match'] = list(matched)[:50]  # Top 50
            keywords_analysis['missing_keywords'] = list(jd_words - resume_words)[:20]  # Top 20 missing
        
        keywords_analysis['total_keywords_found'] = len(keywords_analysis['technical_skills']) + \
                                                    len(keywords_analysis['soft_skills'])
        
        return keywords_analysis
    
    def _check_format(self):
        """Check for ATS-friendly formatting."""
        issues = []
        
        # Check resume length (too short or too long)
        word_count = len(self.resume_text.split())
        if word_count < 200:
            issues.append("Resume is too short (less than 200 words)")
        elif word_count > 1500:
            issues.append("Resume might be too long (over 1500 words)")
        
        # Check for common ATS-incompatible elements
        if 'table' in self.resume_text or 'image' in self.resume_text:
            issues.append("May contain tables or images that ATS systems can't parse")
        
        # Check for section headers
        if not any(section in self.resume_text for section in self.REQUIRED_SECTIONS):
            issues.append("Missing standard section headers")
        
        # Check for consistent formatting
        if len(re.findall(r'\d{4}', self.resume_text)) < 2:
            issues.append("Missing or unclear dates in experience/education")
        
        return issues
    
    def _extract_contact_info(self):
        """Extract contact information."""
        contact = {
            'email': None,
            'phone': None,
            'linkedin': None,
            'github': None,
        }
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, self.resume_text)
        if emails:
            contact['email'] = emails[0]
        
        # Phone
        phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
        phones = re.findall(phone_pattern, self.resume_text)
        if phones:
            contact['phone'] = phones[0]
        
        # LinkedIn
        if 'linkedin.com' in self.resume_text:
            contact['linkedin'] = True
        
        # GitHub
        if 'github.com' in self.resume_text:
            contact['github'] = True
        
        return contact
    
    def _calculate_scores(self):
        """Calculate various scores."""
        # Format Score (0-100)
        format_score = 100
        format_score -= len(self.analysis_results['format_issues']) * 10
        self.analysis_results['format_score'] = max(0, min(100, format_score))
        
        # Content Score (0-100)
        sections = self.analysis_results['sections']
        required_sections_count = sum(sections.get(s, False) for s in self.REQUIRED_SECTIONS)
        optional_sections_count = sum(sections.get(s, False) for s in self.OPTIONAL_SECTIONS)
        
        content_score = (required_sections_count / len(self.REQUIRED_SECTIONS)) * 70
        content_score += (optional_sections_count / len(self.OPTIONAL_SECTIONS)) * 30
        self.analysis_results['content_score'] = round(content_score, 1)
        
        # Keyword Score (0-100)
        keywords = self.analysis_results['keywords']
        total_keywords = keywords['total_keywords_found']
        keyword_score = min(100, total_keywords * 5)  # 5 points per keyword, max 100
        
        if self.job_description:
            # Bonus for job description match
            match_count = len(keywords.get('job_description_match', []))
            keyword_score = min(100, (match_count / 50) * 100)  # Based on top 50 matches
        
        self.analysis_results['keyword_score'] = round(keyword_score, 1)
        
        # ATS Score (combination of all)
        ats_score = (
            self.analysis_results['format_score'] * 0.3 +
            self.analysis_results['content_score'] * 0.3 +
            self.analysis_results['keyword_score'] * 0.4
        )
        self.analysis_results['ats_score'] = round(ats_score, 1)
        
        # Overall Score
        self.analysis_results['overall_score'] = round(ats_score, 1)
    
    def _generate_suggestions(self):
        """Generate actionable suggestions."""
        suggestions = []
        strengths = []
        weaknesses = []
        
        # Check sections
        sections = self.analysis_results['sections']
        if not sections.get('summary'):
            suggestions.append("Add a professional summary at the top highlighting your key strengths")
            weaknesses.append("Missing professional summary")
        else:
            strengths.append("Has professional summary")
        
        if not sections.get('projects'):
            suggestions.append("Add a Projects section to showcase your work")
        
        # Check keywords
        keywords = self.analysis_results['keywords']
        if keywords['total_keywords_found'] < 10:
            suggestions.append("Include more relevant technical skills and keywords")
            weaknesses.append("Low keyword density")
        else:
            strengths.append(f"Good keyword usage ({keywords['total_keywords_found']} keywords found)")
        
        # Check format issues
        if self.analysis_results['format_issues']:
            for issue in self.analysis_results['format_issues']:
                suggestions.append(f"Fix: {issue}")
                weaknesses.append(issue)
        else:
            strengths.append("ATS-friendly format")
        
        # Check contact info
        contact = self.analysis_results['contact_info']
        if not contact['email']:
            suggestions.append("Add your email address")
            weaknesses.append("Missing email")
        if not contact['linkedin']:
            suggestions.append("Add your LinkedIn profile URL")
        if not contact['github'] and 'engineer' in self.job_field:
            suggestions.append("Add your GitHub profile to showcase your code")
        
        # Job description matching
        if self.job_description and keywords.get('missing_keywords'):
            missing = keywords['missing_keywords'][:5]
            suggestions.append(f"Add these job description keywords: {', '.join(missing)}")
        
        # Quantification
        if len(re.findall(r'\d+%', self.resume_text)) < 3:
            suggestions.append("Quantify your achievements with numbers and percentages")
            weaknesses.append("Lacks quantified achievements")
        else:
            strengths.append("Good use of quantified achievements")
        
        # Action verbs
        action_verbs = ['led', 'managed', 'developed', 'created', 'improved', 'increased', 'built']
        action_count = sum(verb in self.resume_text for verb in action_verbs)
        if action_count < 3:
            suggestions.append("Use strong action verbs (Led, Managed, Developed, etc.)")
            weaknesses.append("Lacks strong action verbs")
        else:
            strengths.append("Uses strong action verbs")
        
        self.analysis_results['suggestions'] = suggestions[:15]  # Top 15
        self.analysis_results['strengths'] = strengths
        self.analysis_results['weaknesses'] = weaknesses
    
    def _error_result(self, message):
        """Return error result."""
        return {
            'ats_score': 0,
            'keyword_score': 0,
            'format_score': 0,
            'content_score': 0,
            'overall_score': 0,
            'error': message,
            'suggestions': [message],
            'strengths': [],
            'weaknesses': [],
        }
    
    def generate_report(self):
        """Generate detailed text report."""
        results = self.analysis_results
        
        report = f"""
═══════════════════════════════════════════════════════════
                RESUME ANALYSIS REPORT
═══════════════════════════════════════════════════════════

📊 OVERALL SCORE: {results['overall_score']}/100

📈 SCORE BREAKDOWN:
   • ATS Compatibility: {results['ats_score']}/100
   • Keyword Match:     {results['keyword_score']}/100
   • Format Quality:    {results['format_score']}/100
   • Content Quality:   {results['content_score']}/100

✅ STRENGTHS ({len(results['strengths'])}):
{self._format_list(results['strengths'])}

❌ AREAS TO IMPROVE ({len(results['weaknesses'])}):
{self._format_list(results['weaknesses'])}

💡 ACTIONABLE SUGGESTIONS ({len(results['suggestions'])}):
{self._format_list(results['suggestions'], numbered=True)}

📝 KEYWORDS FOUND ({results['keywords']['total_keywords_found']}):
   • Technical Skills: {', '.join(results['keywords']['technical_skills'][:10])}
   • Soft Skills: {', '.join(results['keywords']['soft_skills'][:5])}

📄 RESUME STATISTICS:
   • Total Words: {results['word_count']}
   • Contact Info: {'✓' if results['contact_info']['email'] else '✗'} Email, {'✓' if results['contact_info']['phone'] else '✗'} Phone
   • LinkedIn: {'✓' if results['contact_info']['linkedin'] else '✗'}
   • GitHub: {'✓' if results['contact_info']['github'] else '✗'}

═══════════════════════════════════════════════════════════
        """
        
        return report.strip()
    
    def _format_list(self, items, numbered=False):
        """Format list for report."""
        if not items:
            return "   None"
        
        formatted = []
        for i, item in enumerate(items, 1):
            prefix = f"   {i}. " if numbered else "   • "
            formatted.append(f"{prefix}{item}")
        
        return '\n'.join(formatted)

