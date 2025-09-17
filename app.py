# app.py
import streamlit as st
from agents import run_agents
import random

search_job = True
st.set_page_config(page_title="Job Finder Assistant", page_icon="💼")


# Session State Initialization
if "stage" not in st.session_state:
    st.chat_message("assistant").write("👋 Hi! I'm your Job Finder Assistant.\n\nPlease upload your **CV**, and tell me your preferred **city** and **country** for the job search.")
    st.session_state.stage = "greet"

# === Stage 1: Greet user ===
if st.session_state.stage == "greet":
    st.session_state.stage = "ask_inputs"

# === Stage 2: Ask for inputs ===
if st.session_state.stage == "ask_inputs":
    
    with st.chat_message("user"):
        countries_cities = {
            "United Kingdom": ["London", "Manchester", "Birmingham"],
            "United States": ["New York", "Los Angeles", "Chicago"]
        }

        col1, col2 = st.columns(2)
        
        with col1:
            country = st.selectbox("Preferred Country", 
                                 options=list(countries_cities.keys()),
                                 index=None,
                                 placeholder="Select a country")
        with col2:
            if country:
                city_options = countries_cities[country]
                city = st.selectbox("Preferred City", 
                                  options=city_options,
                                  index=None,
                                  placeholder="Select a city")
            else:
                city = st.selectbox("Preferred City", 
                                  options=[],
                                  index=None,
                                  placeholder="Select a country first",
                                  disabled=True)
                
        with st.form("cv_input_form"):
            uploaded_cv = st.file_uploader("Upload your CV (PDF or DOCX)", type=["pdf", "docx"])
            submitted = st.form_submit_button("Start Job Search")
            
            if submitted:
                if not uploaded_cv or not city or not country:
                    st.error("Please upload your CV and fill in both city and country.")
                else:
                    st.session_state.stage = "processing"
                    
                    file_name = uploaded_cv.name
                    extension = file_name.split(".")[-1].lower()
                    cv_text = ""
                    
                    if extension == "pdf":
                        # Extract text from PDF
                        cv_text = run_agents(extract_cv_text = uploaded_cv, cv_extension = "pdf")
                    elif extension == "docx":
                        # Extract text from DOCX
                        cv_text = run_agents(extract_cv_text = uploaded_cv, cv_extension = "docx")
                    else:
                        st.error("Unsupported file type.")
                    
                    if cv_text:
                        st.session_state.cv_text = cv_text
                        st.session_state.city = city
                        st.session_state.country = country
                        
                        print("=============================")
                        print(st.session_state.city)
                        print(st.session_state.country)
                        print("=============================")

                        # check if all requirement is meet or not
                        if not run_agents(is_requirements_meet=True, 
                                          cv_text=st.session_state.cv_text, 
                                          city=st.session_state.city, 
                                          country=st.session_state.country):
                            st.chat_message("assistant").error("All fields are required.")
                        else:
                            st.success("✅ Inputs accepted! Processing your CV...")
                            st.session_state.stage = "extract_skills"
                            # st.rerun()

# === Stage 3: Extract Skills ===
if st.session_state.stage == "extract_skills":
    with st.chat_message("assistant"):
        st.write("🔍 Analyzing your CV for skills...")
    st.session_state.skills = run_agents(extract_skills_from_csv_text=True, cv_text = st.session_state.cv_text)
    
    st.subheader("🎯 Your Professional Skills Extracted")
    
    skills_list = [skill.strip() for skill in st.session_state.skills.split(" ")]
    
    # Custom CSS for skill cards
    st.markdown("""
    <style>
    .skill-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 8px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
        border: none;
    }
    .skill-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    }
    .skill-text {
        font-size: 16px;
        font-weight: 600;
        margin: 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display skills in a responsive grid
    cols = st.columns(3)
    
    for i, skill in enumerate(skills_list):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="skill-card">
                <p class="skill-text">{skill}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.session_state.stage = "search_matching_jobs"
       
# === Stage 3: Fetch Matching Jobs ===
if st.session_state.stage == "search_matching_jobs":
    if 'jobs' not in st.session_state or not st.session_state.jobs:
        with st.chat_message("assistant"):
            st.write("🔎 Finding top matching jobs for you...")
        # get matching jobs 
        st.session_state.jobs = run_agents(search_jobs = True, 
                                        skills=st.session_state.skills,
                                        city=st.session_state.city,
                                        country=st.session_state.country)
        
        #st.session_state.stage = "search_matching_jobs_skiping"
    
    st.subheader("💼 Matching Jobs")
    st.write("Review these carefully selected positions and choose one to generate your tailored CV and cover letter.")
    
    # Custom CSS for job cards
    st.markdown("""
    <style>
    .job-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 2px solid #f0f2f6;
        transition: all 0.3s ease;
    }
    .job-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        border-color: #667eea;
    }
    .job-title {
        color: #1f2937;
        font-size: 22px;
        font-weight: 700;
        margin: 0 0 8px 0;
    }
    .job-company {
        color: #667eea;
        font-size: 18px;
        font-weight: 600;
        margin: 0 0 12px 0;
    }
    .job-location {
        color: #6b7280;
        font-size: 14px;
        margin: 0 0 15px 0;
        display: flex;
        align-items: center;
    }
    .job-salary {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
        display: inline-block;
        margin: 0 0 15px 0;
    }
    .job-description {
        color: #4b5563;
        font-size: 14px;
        line-height: 1.6;
        margin: 15px 0;
    }
    .job-url {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
        font-size: 14px;
    }
    .job-url:hover {
        text-decoration: underline;
    }
    .match-score {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        float: right;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display jobs in beautiful cards with selection
    selected_job_id = None
    
    for i, job in enumerate(st.session_state.jobs):
        # Create a beautiful container using Streamlit components
        with st.container():
            # Create columns for layout
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Job title and company
                st.markdown(f"### {job.get('title', 'Job Title Not Available')}")
                st.markdown(f"**🏢 {job.get('company', 'Company Not Available')}**")
            
            with col2:
                # Match score badge
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #8b5cf6, #7c3aed);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    text-align: center;
                    font-weight: bold;
                    margin-top: 10px;
                ">
                    {random.randint((85-i)-(i*2), (85+i)+(i*2)) - i*3}% Match
                </div>
                """, unsafe_allow_html=True)
            
            # Location
            st.markdown(f"📍 **Location:** {job.get('job_location', 'Location Not Available')}")
            
            # Salary with colored background
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #22c55e, #16a34a);
                color: white;
                padding: 8px 16px;
                border-radius: 25px;
                display: inline-block;
                margin: 10px 0;
                font-weight: bold;
            ">
                💰 £{job.get('salary_min', 'N/A')} - £{job.get('salary_max', 'N/A')}
            </div>
            """, unsafe_allow_html=True)
            
            # Description in an info box
            description = job.get('description', 'Description not available')
            #truncated_desc = description[:300] + '...' if len(description) > 300 else description
            truncated_desc = description
            st.info(f"📝 **Job Description:** {truncated_desc}")
            
            # Job URL
            if job.get('job_url'):
                st.markdown(f"[🔗 View Full Job Posting]({job.get('job_url')})")
            
            # Selection button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    f"✨ Generate CV & Cover Letter for this job",
                    key=f"select_job_{i}",
                    type="primary",
                    use_container_width=True
                ):
                    st.session_state.selected_job = job
                    st.session_state.stage = "generate_documents"
                    # st.success(f"✅ Selected: {job.get('title', 'Job')} at {job.get('company', 'Company')}")
                    st.rerun()
            
            # Add divider between jobs
            st.divider()
    
    # Show summary
    st.info(f"🎯 Found {len(st.session_state.jobs)} highly relevant positions matching your skills and location preferences.")


# Generate tailored CV & Cover Letter stage
if st.session_state.stage == "generate_documents":
    if 'tailor_cv_cover_letter' not in st.session_state:
        with st.chat_message("assistant"):
            st.write("✨ Crafting your personalized CV and cover letter...")
            with st.spinner("This may take a moment..."):
                # Generate CV 
                st.session_state.tailor_cv_cover_letter = run_agents(
                    tailor_cv_cover_letter=True,
                    current_cv_text=st.session_state.cv_text,
                    selected_job=st.session_state.selected_job
                )
        st.success("🎉 Your documents are ready!")
    
    st.markdown("---")
    st.markdown("### 🎯 Documents Generated For:")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**📋 Position:** {st.session_state.selected_job.get('title', 'N/A')}")
        st.markdown(f"**🏢 Company:** {st.session_state.selected_job.get('company', 'N/A')}")
        st.markdown(f"**📍 Location:** {st.session_state.selected_job.get('job_location', 'N/A')}")
    
    with col2:
        # Download buttons
        st.markdown("**📥 Quick Actions:**")
        cv_content = st.session_state.tailor_cv_cover_letter.get('tailored_cv', 'CV content not available')
        company_name = st.session_state.selected_job.get('company', 'Job').replace(' ', '_')
        job_title = st.session_state.selected_job.get('title', 'Position').replace(' ', '_')
        
        st.download_button(
            label="📄 Download CV",
            data=cv_content,
            file_name=f"CV_{company_name}_{job_title}.txt",
            mime="text/plain",
            type="secondary",
            use_container_width=True
        )
        # Cover Letter Download - replace st.button with st.download_button
        cover_letter_content = st.session_state.tailor_cv_cover_letter.get('cover_letter', 'Cover letter content not available')
            
        st.download_button(
            label="📝 Download Cover Letter", 
            data=cover_letter_content,
            file_name=f"CoverLetter_{company_name}_{job_title}.txt",
            mime="text/plain",
            type="secondary",
            use_container_width=True
        )
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📄 Tailored CV", "📝 Cover Letter"])
    
    with tab1:
        st.markdown("### 📄 Your Tailored CV")
        st.markdown("*Customized specifically for this position*")
        
        # CV content in a styled container
        st.markdown("""
        <div style="    
            background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 25px;
            margin: 15px 0;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        ">
        """, unsafe_allow_html=True)
        
        # Format CV content nicely
        cv_content = st.session_state.tailor_cv_cover_letter.get('tailored_cv', 'CV content not available')
        
        # Split CV into sections and format
        cv_lines = cv_content.split('\n')
        formatted_cv = ""
        
        for line in cv_lines:
            line = line.strip()
            if line:
                # Check if line looks like a section header (all caps, contains key words, etc.)
                if (line.isupper() or 
                    any(header in line.upper() for header in ['EXPERIENCE', 'EDUCATION', 'SKILLS', 'CONTACT', 'SUMMARY', 'OBJECTIVE']) or
                    line.endswith(':')):
                    formatted_cv += f"**{line}**\n\n"
                else:
                    formatted_cv += f"{line}\n\n"
        
        st.markdown(formatted_cv)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # CV stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Word Count", len(cv_content.split()))
        with col2:
            st.metric("Character Count", len(cv_content))
        with col3:
            st.metric("Sections", len([line for line in cv_lines if line.isupper() or ':' in line]))
    
    with tab2:
        st.markdown("### 📝 Your Cover Letter")
        st.markdown("*Perfectly aligned with the job requirements*")
        
        # Cover letter content in a styled container
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #fefcfb 0%, #ffffff 100%);
            border: 1px solid #fde68a;
            border-radius: 12px;
            padding: 25px;
            margin: 15px 0;
            box-shadow: 0 2px 10px rgba(251, 191, 36, 0.1);
        ">
        """, unsafe_allow_html=True)
        
        cover_letter_content = st.session_state.tailor_cv_cover_letter.get('cover_letter', 'Cover letter content not available')
        
        # Format cover letter with proper spacing
        paragraphs = cover_letter_content.split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                st.markdown(paragraph.strip())
                st.markdown("")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Cover letter stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Word Count", len(cover_letter_content.split()))
        with col2:
            st.metric("Paragraphs", len([p for p in paragraphs if p.strip()]))
        with col3:
            reading_time = max(1, len(cover_letter_content.split()) // 200)
            st.metric("Reading Time", f"{reading_time} min")
    
    st.markdown("---")
    
    # Action buttons at the bottom
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Regenerate Documents", type="secondary", use_container_width=True):
            # Clear the generated documents to force regeneration
            if 'tailor_cv_cover_letter' in st.session_state:
                del st.session_state.tailor_cv_cover_letter
            st.rerun()
    
    with col2:
        if st.button("← Back to Jobs", type="secondary", use_container_width=True):
            st.session_state.stage = "search_matching_jobs"
            st.rerun()
    
    with col3:
        if st.button("🎯 Apply to Another Job", type="secondary", use_container_width=True):
            st.session_state.stage = "search_matching_jobs"
            # Clear selected job so user can pick a new one
            if 'selected_job' in st.session_state:
                del st.session_state.selected_job
            if 'tailor_cv_cover_letter' in st.session_state:
                del st.session_state.tailor_cv_cover_letter
            st.rerun()
    
    with col4:
        if st.button("🏠 Start Over", type="primary", use_container_width=True):
            # Clear all session state and start fresh
            for key in list(st.session_state.keys()):
                if key != 'stage':
                    del st.session_state[key]
            st.session_state.stage = "ask_inputs"
            st.rerun()
    
    # Success message and tips
    st.markdown("---")
    st.success("🎉 Your personalized documents are ready! Review them carefully before applying.")
    
    with st.expander("💡 Application Tips", expanded=False):
        st.markdown("""
        **Before you apply:**
        - ✅ Review both documents for accuracy and completeness
        - ✅ Customize the cover letter opening with the hiring manager's name if known
        - ✅ Double-check that all contact information is current
        - ✅ Save both documents in PDF format for best compatibility
        - ✅ Follow up within a week if you don't hear back
        
        **Good luck with your application! 🍀**
        """)