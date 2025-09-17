# IMPORTS
import utils as ut


def load_prompt(filename):
    with open(f"prompts/{filename}", "r", encoding="utf-8") as f:
        return f.read()

def run_agents(**kwargs):
    # check if function is call for extract text from pdf?
    if "extract_cv_text" in kwargs and kwargs["cv_extension"] == "pdf":
        cv_text = ut.extract_cv_text_from_pdf(kwargs['extract_cv_text'])
        return cv_text
    # check if function is call for extract text from docs?
    elif "extract_cv_text" in kwargs and kwargs["cv_extension"] == "docx":
        cv_text = ut.extract_cv_text_from_docx(kwargs['extract_cv_text'])
        return cv_text
    # check if function is call for requirment check
    
    elif "is_requirements_meet" in kwargs:
        return ut.is_requirements_met(kwargs['cv_text'], kwargs['city'], kwargs['country'])
    # check if function is call for extract skills from csv
    
    elif "extract_skills_from_csv_text" in kwargs:
        # TODO: Need to find way to shorten the text of CV so less number of token will use
        cv_text = kwargs['cv_text']
        # 1. Extract Skills
        # TODO: **
        skills = ut.extract_skills_from_csv_text(cv_text)
        #skills = "Python Sql Data Enginering Airflow Pyspark Databricks ADF"
        print("----------------------------------")
        print("extract skills")
        print("----------------------------------")
        return skills
    elif "search_jobs" in kwargs:
        # Find Jobs first
        jobs = ut.get_jobs_adzuna(skills=kwargs['skills'], city=kwargs['city'], country=kwargs['country'])
        # Now extract most relevant jobs
        
        # TODO: **
        most_relevant_jobs = ut.extract_most_relevant_jobs(skills=kwargs['skills'],
                                                           city=kwargs['city'],
                                                           country=kwargs['country'],
                                                           jobs=jobs,
                                                           n_relevant_jobs=5
                                                           )
        print("----------------------------------")
        print("job search")
        print("----------------------------------")
        
        return most_relevant_jobs
    elif "tailor_cv_cover_letter" in kwargs:
        # tailor_cv_cover_letter, current_cv_text, selected_job
        
        tailored_cv = ut.tailor_current_cv(
            cv_text=kwargs['current_cv_text'],
            job_description=kwargs['selected_job'] 
        )
        cover_letter = ut.generate_cover_letter(
            cv_text=kwargs['current_cv_text'],
            job_description=kwargs['selected_job']
        )
        
        cv_and_cover = {
            "tailored_cv": tailored_cv,
            "cover_letter": cover_letter
        }
        
        return cv_and_cover
