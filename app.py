"""
Smart Resume AI - Main Application
A modern AI-powered resume analysis tool

Author: Tiny Titans

"""

# ============================================================================
# IMPORTS
# ============================================================================

# Standard Library
import os
import json
import base64
from datetime import datetime
from io import BytesIO
from typing import Dict, List, Optional, Any

# Third-Party Libraries
import streamlit as st
import pandas as pd
import docx
import spacy
from streamlit_lottie import st_lottie

# Local Imports
from utils.resume_analyzer import ResumeAnalyzer
from config.job_roles import JOB_ROLES
from config.courses import (
    COURSES_BY_CATEGORY,
    RESUME_VIDEOS,
    INTERVIEW_VIDEOS,
    get_courses_for_role,
    get_category_for_role
)
from ui_components import (
    apply_modern_styles,
    hero_section,
    feature_card,
    about_section,
    page_header
)


# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

PAGE_CONFIG = {
    "page_title": "Smart Resume AI",
    "page_icon": "🚀",
    "layout": "wide"
}

CSS_FILES = ['style/styles_extracted.css']

LOTTIE_ANIMATION_URL = "https://lottie.host/a24ca275-7e0c-4a06-8f2e-82a32af725b3/GRSUqxJajz.json"

FILE_TYPES = {
    'PDF': 'application/pdf',
    'DOCX': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}

ATS_SCORE_THRESHOLDS = {
    'EXCELLENT': 80,
    'GOOD': 60
}


EXTERNAL_FONTS_AND_ICONS = """
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
"""


# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_page_config() -> None:
    """Initialize Streamlit page configuration."""
    st.set_page_config(**PAGE_CONFIG)


def initialize_spacy_model() -> spacy.language.Language:
    """
    Load and initialize the SpaCy NLP model.
    
    Returns:
        Loaded SpaCy model with parser and tagger disabled for performance.
        
    Raises:
        SystemExit: If the SpaCy model is not installed.
    """
    try:
        return spacy.load("en_core_web_sm", disable=["parser", "tagger"])
    except OSError:
        st.error(
            "The SpaCy model 'en_core_web_sm' is not installed. "
            "Please redeploy after adding it to requirements.txt."
        )
        st.stop()


def initialize_environment() -> None:
    """Set up environment variables and configurations."""
    os.environ["STREAMLIT_WATCHER_TYPE"] = "none"


def load_external_resources() -> None:
    """Load external fonts and icon libraries."""
    st.markdown(EXTERNAL_FONTS_AND_ICONS, unsafe_allow_html=True)


# ============================================================================
# MAIN APPLICATION CLASS
# ============================================================================

class ResumeApp:
    """
    Main application class for Smart Resume AI.
    
    Handles navigation, page rendering, and core application logic.
    """
    
    def __init__(self):
        """Initialize the application with default settings and components."""
        self._initialize_session_state()
        self._setup_pages()
        self._initialize_components()
        self._load_resources()
    
    def _initialize_session_state(self) -> None:
        """Initialize session state variables."""
        if 'page' not in st.session_state:
            st.session_state.page = 'home'
        
        if 'is_admin' not in st.session_state:
            st.session_state.is_admin = False
        
        if 'initial_load' not in st.session_state:
            st.session_state.initial_load = True
    
    def _setup_pages(self) -> None:
        """Configure available pages and their render functions."""
        self.pages = {
            "HOME": self.render_home,
            "RESUME ANALYZER": self.render_analyzer,
        }
    
    def _initialize_components(self) -> None:
        """Initialize application components and data structures."""
        self.analyzer = ResumeAnalyzer()
        self.job_roles = JOB_ROLES
    
    def _load_resources(self) -> None:
        """Load all required external resources (CSS, fonts, etc.)."""
        self._load_css_files()
        load_external_resources()
    
    # ========================================================================
    # RESOURCE LOADING
    # ========================================================================
    
    def _load_css_files(self) -> None:
        """Load all external CSS files into the application."""
        for css_file in CSS_FILES:
            try:
                with open(css_file) as f:
                    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
            except FileNotFoundError:
                st.warning(f"CSS file not found: {css_file}")
    
    @staticmethod
    def load_lottie_url(url: str) -> Optional[Dict[str, Any]]:
        """
        Load Lottie animation from a URL.
        
        Args:
            url: URL of the Lottie animation JSON.
            
        Returns:
            Animation data as dictionary, or None if loading fails.
        """
        import requests
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None
    
    # ========================================================================
    # PAGE: HOME
    # ========================================================================
    
    def render_home(self):
        """Render the home/landing page"""
        apply_modern_styles()
        
        # Hero Section
        hero_section(
            "AI QuickScreener",
            "Transform your hiring process with AI-powered resume screening. "
            "Screen hundreds of candidates in minutes, eliminate unconscious bias, "
            "and find the perfect match for every role. Say goodbye to manual resume "
            "reviews and hello to faster, smarter, and more accurate hiring decisions "
            "that help you build exceptional teams."
        )
        
        # Feature Cards
        st.markdown('<div class="feature-grid">', unsafe_allow_html=True)
        
        feature_card(
            "",
            "Intelligent Candidate Screening",
            "Automatically analyze and rank resumes using advanced natural language "
            "processing and machine learning. Our intelligent algorithms evaluate "
            "candidate qualifications, skills, and experience against your job "
            "requirements with precision, saving you hours of manual review time."
        )
        
        feature_card(
            "",
            "Recommendations & Analytics",
            "Get comprehensive analytics and visualizations of your candidate pool. "
            "Understand skill distributions, identify top talent instantly, and make "
            "informed hiring decisions backed by data. Reduce time-to-hire by up to "
            "75% while improving candidate quality."
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Call-to-Action Button
        self._render_cta_button()

    
    def _render_cta_button(self) -> None:
        """Render the call-to-action button on the home page."""
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(
                "Get Started",
                key="get_started_btn",
                help="Click to start analyzing your resume",
                type="primary",
                use_container_width=True
            ):
                self._navigate_to_analyzer()
    
    def _navigate_to_analyzer(self) -> None:
        """Navigate to the resume analyzer page."""
        st.session_state.page = "resume_analyzer"
        st.rerun()
    
    # ========================================================================
    # PAGE: RESUME ANALYZER
    # ========================================================================
    
    def render_analyzer(self) -> None:
        """Render the resume analyzer page."""
        apply_modern_styles()
        
        page_header(
            "Resume Analyzer",
            "Get instant AI-powered feedback to optimize your resume"
        )
        
        # Job Selection
        selected_category, selected_role, role_info = self._render_job_selection()
        
        # Display Role Information
        self._display_role_info(selected_role, role_info)
        
        # File Upload and Analysis
        uploaded_file = st.file_uploader(
            "Upload your resume",
            type=['pdf', 'docx']
        )
        
        if uploaded_file:
            self._handle_file_upload(
                uploaded_file,
                selected_role,
                selected_category,
                role_info
            )
        else:
            st.info("Please upload a resume (PDF or DOCX) to proceed.")
    
    def _render_job_selection(self) -> tuple:
        """
        Render job category and role selection dropdowns.
        
        Returns:
            Tuple of (selected_category, selected_role, role_info)
        """
        categories = list(self.job_roles.keys())
        selected_category = st.selectbox("Job Category", categories)
        
        roles = list(self.job_roles[selected_category].keys())
        selected_role = st.selectbox("Specific Role", roles)
        
        role_info = self.job_roles[selected_category][selected_role]
        
        return selected_category, selected_role, role_info
    
    def _display_role_info(self, selected_role: str, role_info: Dict[str, Any]) -> None:
        """
        Display information about the selected job role.
        
        Args:
            selected_role: Name of the selected role.
            role_info: Dictionary containing role details.
        """
        required_skills = ', '.join(role_info['required_skills'])
        
        st.markdown(f"""
        <div class='role-info-card'>
            <h3>{selected_role}</h3>
            <p>{role_info['description']}</p>
            <h4>Required Skills:</h4>
            <p>{required_skills}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _handle_file_upload(
        self,
        uploaded_file,
        selected_role: str,
        selected_category: str,
        role_info: Dict[str, Any]
    ) -> None:
        """
        Handle the uploaded resume file and trigger analysis.
        
        Args:
            uploaded_file: Streamlit uploaded file object.
            selected_role: Selected job role.
            selected_category: Selected job category.
            role_info: Dictionary containing role details.
        """
        self._display_uploaded_file(uploaded_file)
        self._analyze_uploaded_resume(
            uploaded_file,
            selected_role,
            selected_category,
            role_info
        )
    
    # ========================================================================
    # FILE HANDLING
    # ========================================================================
    
    def _display_uploaded_file(self, uploaded_file) -> None:
        """
        Display the uploaded file with preview and download options.
        
        Args:
            uploaded_file: Streamlit uploaded file object.
        """
        if uploaded_file.type == FILE_TYPES['PDF']:
            self._display_pdf_preview(uploaded_file)
        elif uploaded_file.type == FILE_TYPES['DOCX']:
            st.warning("DOCX files are uploaded but not displayed as embedded PDF.")
        else:
            st.error("Unsupported file format. Please upload PDF or DOCX.")
    
    def _display_pdf_preview(self, uploaded_file) -> None:
        """
        Display PDF preview with download option.
        
        Args:
            uploaded_file: Streamlit uploaded file object (PDF).
        """
        pdf_data = uploaded_file.read()
        
        if pdf_data:
            base64_pdf = base64.b64encode(pdf_data).decode("utf-8")
            
            # Preview Option
            if st.checkbox("Preview Resume (PDF)"):
                pdf_display = (
                    f'<iframe src="data:application/pdf;base64,{base64_pdf}" '
                    f'width="100%" height="700"></iframe>'
                )
                st.markdown(pdf_display, unsafe_allow_html=True)
            
            # Download Button
            st.download_button(
                label="📄 Download Uploaded PDF",
                data=pdf_data,
                file_name="uploaded_resume.pdf",
                mime=FILE_TYPES['PDF']
            )
            
            # Reset file pointer
            uploaded_file.seek(0)
    
    # ========================================================================
    # RESUME ANALYSIS
    # ========================================================================
    
    def _analyze_uploaded_resume(
        self,
        uploaded_file,
        selected_role: str,
        selected_category: str,
        role_info: Dict[str, Any]
    ) -> None:
        """
        Extract text from uploaded file and perform resume analysis.
        
        Args:
            uploaded_file: Streamlit uploaded file object.
            selected_role: Selected job role.
            selected_category: Selected job category.
            role_info: Dictionary containing role details.
        """
        with st.spinner("Analyzing your document..."):
            text = self._extract_text_from_file(uploaded_file)
            
            if not text:
                return
            
            analysis = self.analyzer.analyze_resume(
                {'raw_text': text},
                role_info
            )
            
            # Validate Document Type
            if not self._validate_document_type(analysis):
                return
            
            # Display Results
            self._display_analysis_results(
                analysis,
                selected_role,
                selected_category
            )
    
    def _extract_text_from_file(self, uploaded_file) -> str:
        """
        Extract text content from uploaded file.
        
        Args:
            uploaded_file: Streamlit uploaded file object.
            
        Returns:
            Extracted text as string, empty string on error.
        """
        try:
            uploaded_file.seek(0)
            
            if uploaded_file.type == FILE_TYPES['PDF']:
                return self.analyzer.extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type == FILE_TYPES['DOCX']:
                return self.analyzer.extract_text_from_docx(uploaded_file)
            else:
                return uploaded_file.getvalue().decode()
                
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            return ""
    
    def _validate_document_type(self, analysis: Dict[str, Any]) -> bool:
        """
        Validate that the uploaded document is a resume.
        
        Args:
            analysis: Analysis results dictionary.
            
        Returns:
            True if document is a resume, False otherwise.
        """
        if analysis.get('document_type') != 'resume':
            document_type = analysis.get('document_type', 'unknown')
            st.error(
                f"⚠️ This appears to be a {document_type} document, "
                "not a resume!"
            )
            return False
        return True
    
    # ========================================================================
    # ANALYSIS RESULTS DISPLAY
    # ========================================================================
    
    def _display_analysis_results(
        self,
        analysis: Dict[str, Any],
        selected_role: str,
        selected_category: str
    ) -> None:
        """
        Display comprehensive analysis results.
        
        Args:
            analysis: Analysis results dictionary.
            selected_role: Selected job role.
            selected_category: Selected job category.
        """
        # Score and Skills Section
        col1, col2 = st.columns(2)
        with col1:
            self._render_ats_score_card(analysis)
        with col2:
            self._render_skills_match_card(analysis)
        
        # Course Recommendations
        st.markdown("### 📚 Recommended Courses")
        self._render_course_recommendations(selected_role, selected_category)
        
        # Learning Resources
        st.markdown("### 📺 Helpful Videos")
        self._render_learning_resources()
    
    def _render_ats_score_card(self, analysis: Dict[str, Any]) -> None:
        """
        Render the ATS score card with circular progress indicator.
        
        Args:
            analysis: Analysis results dictionary.
        """
        score = analysis['ats_score']
        color_class = self._get_score_color_class(score)
        
        st.markdown(f"""
        <div class="feature-card">
            <h2>ATS Score</h2>
            <div class="ats-score-container">
                <div class="ats-score-circle" 
                     style="background: conic-gradient(#00ffd5 {score}%, #222 {score}% 100%)">
                    <div class="ats-score-inner {color_class}">{score}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _get_score_color_class(score: int) -> str:
        """
        Determine the color class based on ATS score.
        
        Args:
            score: ATS score value.
            
        Returns:
            CSS class name for score color.
        """
        if score >= ATS_SCORE_THRESHOLDS['EXCELLENT']:
            return 'score-excellent'
        elif score >= ATS_SCORE_THRESHOLDS['GOOD']:
            return 'score-good'
        else:
            return 'score-needs-improvement'
    
    def _render_skills_match_card(self, analysis: Dict[str, Any]) -> None:
        """
        Render the skills match card showing keyword matches and gaps.
        
        Args:
            analysis: Analysis results dictionary.
        """
        st.markdown(
            "<div class='feature-card'><h2>Skills Match</h2>",
            unsafe_allow_html=True
        )
        
        # Keyword Match Percentage
        keyword_score = int(analysis.get('keyword_match', {}).get('score', 0))
        st.metric("Keyword Match", f"{keyword_score}%")
        
        # Missing Skills
        missing_skills = analysis['keyword_match'].get('missing_skills', [])
        if missing_skills:
            st.markdown("#### Missing Skills:")
            for skill in missing_skills:
                st.markdown(f"- {skill}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ========================================================================
    # RECOMMENDATIONS
    # ========================================================================
    
    def _render_course_recommendations(
        self,
        selected_role: str,
        selected_category: str
    ) -> None:
        """
        Render course recommendations based on selected role.
        
        Args:
            selected_role: Selected job role.
            selected_category: Selected job category.
        """
        courses = self._get_relevant_courses(selected_role, selected_category)
        
        if not courses:
            st.info("No specific courses found for this role.")
            return
        
        # Display courses in two columns
        cols = st.columns(2)
        for i, course in enumerate(courses[:6]):
            with cols[i % 2]:
                self._render_course_card(course)
    
    def _get_relevant_courses(
        self,
        selected_role: str,
        selected_category: str
    ) -> List[tuple]:
        """
        Get relevant courses for the selected role.
        
        Args:
            selected_role: Selected job role.
            selected_category: Selected job category.
            
        Returns:
            List of course tuples (name, url).
        """
        courses = get_courses_for_role(selected_role)
        
        if not courses:
            category = get_category_for_role(selected_role)
            courses = COURSES_BY_CATEGORY.get(category, {}).get(selected_role, [])
        
        return courses
    
    @staticmethod
    def _render_course_card(course: tuple) -> None:
        """
        Render a single course card.
        
        Args:
            course: Tuple of (course_name, course_url).
        """
        course_name, course_url = course
        st.markdown(f"""
        <div class="course-card">
            <h4>{course_name}</h4>
            <a href='{course_url}' target='_blank'>View Course</a>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_learning_resources(self) -> None:
        """Render learning resource videos in tabbed interface."""
        tab1, tab2 = st.tabs(["Resume Tips", "Interview Tips"])
        
        with tab1:
            self._render_video_section(RESUME_VIDEOS)
        
        with tab2:
            self._render_video_section(INTERVIEW_VIDEOS)
    
    @staticmethod
    def _render_video_section(videos_dict: Dict[str, List[tuple]]) -> None:
        """
        Render a section of videos organized by category.
        
        Args:
            videos_dict: Dictionary mapping categories to video lists.
        """
        for category, videos in videos_dict.items():
            st.subheader(category)
            cols = st.columns(2)
            
            for i, video in enumerate(videos):
                with cols[i % 2]:
                    video_title, video_url = video
                    st.video(video_url)
    
    # ========================================================================
    # NAVIGATION
    # ========================================================================
    
    def _render_sidebar(self) -> None:
        """Render the sidebar with navigation and branding."""
        with st.sidebar:
            # Lottie Animation
            animation_data = self.load_lottie_url(LOTTIE_ANIMATION_URL)
            if animation_data:
                st_lottie(animation_data, height=200, key="sidebar_animation")
            
            # Title
            st.title("Smart Resume AI")
            st.markdown("---")
            
            # Navigation Buttons
            for page_name in self.pages.keys():
                if st.button(page_name, use_container_width=True):
                    self._navigate_to_page(page_name)
    
    def _navigate_to_page(self, page_name: str) -> None:
        """
        Navigate to a specific page.
        
        Args:
            page_name: Name of the page to navigate to.
        """
        cleaned_name = self._clean_page_name(page_name)
        st.session_state.page = cleaned_name
        st.rerun()
    
    @staticmethod
    def _clean_page_name(page_name: str) -> str:
        """
        Clean page name for session state storage.
        
        Args:
            page_name: Original page name.
            
        Returns:
            Cleaned page name.
        """
        return (page_name.lower()
                .replace(" ", "_")
                .replace("🔍", "")
                .replace("🏠", "")
                .strip())
    
    def _get_current_page_renderer(self) -> callable:
        """
        Get the render function for the current page.
        
        Returns:
            Page render function.
        """
        current_page = st.session_state.get('page', 'home')
        
        page_mapping = {
            self._clean_page_name(name): name
            for name in self.pages.keys()
        }
        
        if current_page in page_mapping:
            return self.pages[page_mapping[current_page]]
        else:
            return self.render_home
    
    # ========================================================================
    # MAIN EXECUTION
    # ========================================================================
    
    def main(self) -> None:
        """Main application entry point."""
        # Render Sidebar
        self._render_sidebar()
        
        # Handle Initial Load
        if st.session_state.get('initial_load'):
            st.session_state.initial_load = False
            st.session_state.page = 'home'
            st.rerun()
        
        # Render Current Page
        page_renderer = self._get_current_page_renderer()
        page_renderer()


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

def main():
    """Initialize and run the Smart Resume AI application."""
    # Environment Setup
    initialize_environment()
    
    # Page Configuration
    initialize_page_config()
    
    # Initialize SpaCy
    nlp = initialize_spacy_model()
    
    # Create and Run Application
    app = ResumeApp()
    app.main()


if __name__ == "__main__":
    main()
