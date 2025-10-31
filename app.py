import streamlit as st
import os
import base64
import spacy

# Disable file watcher for production
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

# Import custom modules
from streamlit_lottie import st_lottie
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


class ResumeApp:
    """Main application class for Smart Resume AI"""

    def __init__(self):
        """Initialize the application with default settings and configurations"""
        self._initialize_session_state()
        self._setup_application()
        self._load_resources()

    def _initialize_session_state(self):
        """Initialize session state variables"""
        if 'page' not in st.session_state:
            st.session_state.page = 'home'
        if 'is_admin' not in st.session_state:
            st.session_state.is_admin = False

    def _setup_application(self):
        """Setup application configurations"""
        self.pages = {
            "HOME": self.render_home,
            "ANALYZE RESUME": self.render_analyzer,
        }
        self.analyzer = ResumeAnalyzer()
        self.job_roles = JOB_ROLES

    def _load_resources(self):
        """Load external resources (CSS, fonts, SpaCy model)"""
        self._load_spacy_model()
        self._load_css_files()
        self._load_external_fonts()

    def _load_spacy_model(self):
        """Load SpaCy NLP model"""
        try:
            self.nlp = spacy.load("en_core_web_sm", disable=["parser", "tagger"])
        except OSError:
            st.error("The SpaCy model 'en_core_web_sm' is not installed. "            )
            st.stop()

    def _load_css_files(self):
        """Load all external CSS files"""
        css_files = ['style/styles_extracted.css']
        for css_file in css_files:
            try:
                with open(css_file) as f:
                    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
            except FileNotFoundError:
                st.warning(f"CSS file not found: {css_file}")

    def _load_external_fonts(self):
        """Load Google Fonts and Font Awesome icons"""
        st.markdown("""
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        """, unsafe_allow_html=True)

    @staticmethod
    def load_lottie_url(url: str):
        """Load Lottie animation from URL"""
        import requests
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        return None

    # =====================================
    # PAGE RENDERING METHODS
    # =====================================

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

    def _render_cta_button(self):
        """Render the call-to-action button"""
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(
                "Start Screening",
                key="get_started_btn",
                help="Click to start analyzing your resume",
                type="primary",
                use_container_width=True
            ):
                st.session_state.page = "analyze_resume"
                st.rerun()

    def render_analyzer(self):
        """Render the resume analyzer page"""
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

    def _render_job_selection(self):
        """Render job category and role selection"""
        categories = list(self.job_roles.keys())
        selected_category = st.selectbox("Job Category", categories)
        
        roles = list(self.job_roles[selected_category].keys())
        selected_role = st.selectbox("Specific Role", roles)
        
        role_info = self.job_roles[selected_category][selected_role]
        
        return selected_category, selected_role, role_info

    def _display_role_info(self, selected_role, role_info):
        """Display information about the selected role"""
        st.markdown(f"""
        <div class='role-info-card'>
            <h3>{selected_role}</h3>
            <p>{role_info['description']}</p>
            <h4>Required Skills:</h4>
            <p>{', '.join(role_info['required_skills'])}</p>
        </div>
        """, unsafe_allow_html=True)

    # =====================================
    # FILE HANDLING METHODS
    # =====================================

    def _handle_file_upload(self, uploaded_file, selected_role, selected_category, role_info):
        """Handle uploaded file processing and analysis"""
        self._display_uploaded_file(uploaded_file)
        self._analyze_uploaded_resume(
            uploaded_file,
            selected_role,
            selected_category,
            role_info
        )

    def _display_uploaded_file(self, uploaded_file):
        """Display and provide download option for uploaded file"""
        if uploaded_file.type == "application/pdf":
            self._handle_pdf_display(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            st.warning("DOCX files are uploaded but not displayed as embedded PDF.")
        else:
            st.error("Unsupported file format. Please upload PDF or DOCX.")

    def _handle_pdf_display(self, uploaded_file):
        """Handle PDF file display and download"""
        pdf_data = uploaded_file.read()
        if pdf_data:
            base64_pdf = base64.b64encode(pdf_data).decode("utf-8")
            
            if st.checkbox("Preview Resume (PDF)"):
                pdf_display = (
                    f'<iframe src="data:application/pdf;base64,{base64_pdf}" '
                    f'width="100%" height="700"></iframe>'
                )
                st.markdown(pdf_display, unsafe_allow_html=True)
            
            st.download_button(
                label="📄 Download Uploaded PDF",
                data=pdf_data,
                file_name="uploaded_resume.pdf",
                mime="application/pdf"
            )
            
            uploaded_file.seek(0)

    def _analyze_uploaded_resume(self, uploaded_file, selected_role, selected_category, role_info):
        """Analyze the uploaded resume"""
        with st.spinner("Analyzing your document..."):
            # Extract text from file
            text = self._extract_text_from_file(uploaded_file)
            
            if not text:
                return
            
            # Perform analysis
            analysis = self.analyzer.analyze_resume({'raw_text': text}, role_info)
            
            # Validate document type
            if analysis.get('document_type') != 'resume':
                st.error(
                    f"⚠️ This appears to be a {analysis['document_type']} document, "
                    f"not a resume!"
                )
                return
            
            # Display results
            self._display_analysis_results(analysis, selected_role, selected_category)

    def _extract_text_from_file(self, uploaded_file):
        """Extract text from uploaded file"""
        try:
            uploaded_file.seek(0)
            
            if uploaded_file.type == "application/pdf":
                return self.analyzer.extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return self.analyzer.extract_text_from_docx(uploaded_file)
            else:
                return uploaded_file.getvalue().decode()
                
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            return None

    # =====================================
    # ANALYSIS RESULTS DISPLAY METHODS
    # =====================================

    def _display_analysis_results(self, analysis, selected_role, selected_category):
        """Display complete analysis results"""
        # Score Cards
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

    def _render_ats_score_card(self, analysis):
        """Render ATS score card with visual indicator"""
        score = analysis['ats_score']
        
        if score >= 80:
            color_class = 'score-excellent'
        elif score >= 60:
            color_class = 'score-good'
        else:
            color_class = 'score-needs-improvement'
        
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

    def _render_skills_match_card(self, analysis):
        """Render skills match card"""
        st.markdown("""
        <div class="feature-card">
            <h2>Skills Match</h2>
        """, unsafe_allow_html=True)
        
        keyword_match = analysis.get('keyword_match', {})
        st.metric("Keyword Match", f"{int(keyword_match.get('score', 0))}%")
        
        missing_skills = keyword_match.get('missing_skills', [])
        if missing_skills:
            st.markdown("#### Missing Skills:")
            for skill in missing_skills:
                st.markdown(f"- {skill}")
        
        st.markdown("</div>", unsafe_allow_html=True)

    def _render_course_recommendations(self, selected_role, selected_category):
        """Render course recommendations"""
        courses = get_courses_for_role(selected_role)
        
        if not courses:
            category = get_category_for_role(selected_role)
            courses = COURSES_BY_CATEGORY.get(category, {}).get(selected_role, [])
        
        cols = st.columns(2)
        for i, course in enumerate(courses[:6]):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="course-card">
                    <h4>{course}</h4>
                    <a href='{course}' target='_blank'>View Course</a>
                </div>
                """, unsafe_allow_html=True)

    def _render_learning_resources(self):
        """Render video learning resources"""
        tab1, tab2 = st.tabs(["Resume Tips", "Interview Tips"])
        
        with tab1:
            self._render_video_category(RESUME_VIDEOS)
        
        with tab2:
            self._render_video_category(INTERVIEW_VIDEOS)

    def _render_video_category(self, videos_dict):
        """Render videos for a specific category"""
        for category, videos in videos_dict.items():
            st.subheader(category)
            cols = st.columns(2)
            for i, video in enumerate(videos):
                with cols[i % 2]:
                    st.video(video)

    # =====================================
    # NAVIGATION AND MAIN METHODS
    # =====================================

    def _render_sidebar(self):
        """Render sidebar navigation"""
        with st.sidebar:
            # Lottie Animation
            st_lottie(
                self.load_lottie_url(
                    "https://lottie.host/a24ca275-7e0c-4a06-8f2e-82a32af725b3/GRSUqxJajz.json"
                ),
                height=200,
                key="sidebar_animation"
            )
            
            st.title("AI QuickScreener")
            st.markdown("---")
            
            # Navigation Buttons
            for page_name in self.pages.keys():
                if st.button(page_name, use_container_width=True):
                    cleaned_name = self._clean_page_name(page_name)
                    st.session_state.page = cleaned_name
                    st.rerun()

    @staticmethod
    def _clean_page_name(page_name):
        """Clean page name for routing"""
        return page_name.lower().replace(" ", "_").strip()

    def _get_current_page_function(self):
        """Get the function for the current page"""
        current_page = st.session_state.get('page', 'home')
        
        # Create page mapping
        page_mapping = {
            self._clean_page_name(name): name
            for name in self.pages.keys()
        }
        
        if current_page in page_mapping:
            return self.pages[page_mapping[current_page]]
        else:
            return self.render_home

    def main(self):
        """Main application entry point"""
        # Handle initial load
        if 'initial_load' not in st.session_state:
            st.session_state.initial_load = True
            st.session_state.page = 'home'
            st.rerun()
        
        # Render sidebar
        self._render_sidebar()
        
        # Render current page
        current_page_function = self._get_current_page_function()
        current_page_function()


# =====================================
# APPLICATION ENTRY POINT
# =====================================

if __name__ == "__main__":
    app = ResumeApp()
    app.main()
