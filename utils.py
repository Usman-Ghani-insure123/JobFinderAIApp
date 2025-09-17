import os
import ast
# from langchain.llms import LlamaCpp
from langchain.chains import LLMChain
#from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import AzureChatOpenAI
import prompts.prompts_template as prom
from docx import Document

from dotenv import load_dotenv
load_dotenv()


def get_llm_model(openai_api_key, azure_endpoint, deployment_name, api_version, temperature):
    try:
        llm_model = AzureChatOpenAI(
                openai_api_key=os.getenv(openai_api_key),
                azure_endpoint=os.getenv(azure_endpoint),
                deployment_name=os.getenv(deployment_name),
                api_version=os.getenv(api_version),
                temperature=temperature)
        
        return llm_model
    except Exception as e:
        print(f"\033Got error file getting llm model: {e} \033[0m")
        return None

def extract_skills_from_csv_text(cv_text):
    parse_prompt = ChatPromptTemplate.from_messages([
            ("system", prom.extract_skills_from_cv_text_prompt_system),
            ("human", prom.extract_skills_from_cv_text_prompt_human)
        ])
    gpt_4o_mini = get_llm_model(
        openai_api_key="gpt_4_o_mini_AZURE_OPENAI_KEY",
        azure_endpoint="gpt_4_o_mini_AZURE_OPENAI_ENDPOINT",
        deployment_name="gpt_4_o_mini_AZURE_OPENAI_DEPLOYMENT_NAME",
        api_version="gpt_4_o_mini_AZURE_OPENAI_API_VERSION",
        temperature=0.3
    )
    
    parse_chain = LLMChain(llm=gpt_4o_mini, prompt=parse_prompt)    
    skills = parse_chain.run({"cv_text": cv_text})
    return skills

def read_cv_file(uploaded_file):
    content = uploaded_file.read()
    return content.decode("utf-8", errors="ignore")

def extract_cv_text_from_pdf(file):
    import fitz  # PyMuPDF
    
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_cv_text_from_docx(file):
    doc = Document(file)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return "\n".join(full_text)

def is_requirements_met(cv_text: str, city: str, country: str) -> bool:
    return all([
        isinstance(cv_text, str) and cv_text.strip(),
        isinstance(city, str) and city.strip(),
        isinstance(country, str) and country.strip(),
    ])

def get_jobs_adzuna(skills, city, country):
    import os
    import requests
    import urllib.parse
    
    ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs"
    RESULT_PER_PAGE = 100
    
    if not skills or not city or not country:
        raise ValueError("Skills, city, and country are required.")
    
    country_maping = {
        "United Kingdom": {"map_in_url": "gb", "map_in_param": "uk"},
        "United States": {"map_in_url": "us",  "map_in_param": "us"},
    }
    city_mapping = {
        "London": "London",
        "Manchester": "North West England",
        "Birmingham": "West Midlands",
        
        "New York": "New York",
        "Los Angeles": "California",
        "Chicago": "Illinois"
    }
    
    country_url_str = country_maping[country]['map_in_url']
    countr_parm_str = country_maping[country]['map_in_param']
    city_parm_str = city_mapping[city]
    
    encoded_query = urllib.parse.quote(skills)
    encoded_country = urllib.parse.quote(countr_parm_str)
    encoded_city = urllib.parse.quote(city_parm_str)


    # Final API URL
    url = (
        f"{ADZUNA_BASE_URL}/{country_url_str}/search/1"
        f"?app_id={os.getenv('ADZUNA_APP_ID')}"
        f"&app_key={os.getenv('ADZUNA_API_KEY')}" 
        f"&results_per_page={RESULT_PER_PAGE}"
        f"&what_or={encoded_query}"
        f"&location0={encoded_country}"
        f"&location1={encoded_city}")
    
    
    print('\033[36m' + "url " + url)
    
    response = requests.get(url)
    
    if response.status_code == 200:
        parsed_jobs = parse_jobs(response.json())
        return parsed_jobs
    else:
        raise RuntimeError(f"Adzuna API failed: {response.status_code} - {response.text}")

def parse_jobs(raw_jobs):
    parsed_jobs = []
    if raw_jobs['count'] > 0:
        job_index = 1
        for job in raw_jobs['results']:
            job_dic = dict()
            
            job_dic['job_id'] = job_index
            job_dic['title'] = job.get('title', None)
            job_dic['description'] = job.get('description', None)
            job_dic['company'] = job.get('company', None).get('display_name', None)
            job_dic['salary_max'] = job.get('salary_max', None)
            job_dic['salary_min'] = job.get('salary_min', None)
            job_dic['job_created_date'] = job.get('created', None)
            job_dic['job_category'] = job.get('category', None).get('label', None)
            job_dic['job_url'] = job.get('redirect_url', None)
            job_dic['job_location'] = job.get('location', None).get('display_name', None)
            job_dic['location_latitude'] = job.get('latitude', None)
            job_dic['location_longitude'] = job.get('longitude', None)
            
            parsed_jobs.append(job_dic)
            job_index += 1
            
    return parsed_jobs


def extract_most_relevant_jobs(skills, city, country, jobs, n_relevant_jobs=5):
    parse_prompt = ChatPromptTemplate.from_messages([
                ("system", prom.extract_most_rel_jobs_prompt_system.format(n_jobs=n_relevant_jobs)),
                ("human", prom.extract_most_rel_jobs_prompt_human)
            ])
    gpt_4o_mini = get_llm_model(
            openai_api_key="gpt_4_o_mini_AZURE_OPENAI_KEY",
            azure_endpoint="gpt_4_o_mini_AZURE_OPENAI_ENDPOINT",
            deployment_name="gpt_4_o_mini_AZURE_OPENAI_DEPLOYMENT_NAME",
            api_version="gpt_4_o_mini_AZURE_OPENAI_API_VERSION",
            temperature=0.3
        )
        
    parse_chain = LLMChain(llm=gpt_4o_mini, prompt=parse_prompt)    
    most_rel_jobs = parse_chain.run({
                                        "skills": skills,
                                        "n_jobs": n_relevant_jobs,
                                        "jobs": jobs
                                    })

    jobs_list = ast.literal_eval(most_rel_jobs)
    
    return jobs_list


def tailor_current_cv(cv_text, job_description):
    parse_prompt = ChatPromptTemplate.from_messages([
        ("system", prom.tailor_cv_prompt_system),
    (   "human", prom.tailor_cv_prompt_human)
    ])

    gpt_4o_mini = get_llm_model(
            openai_api_key="gpt_4_o_mini_AZURE_OPENAI_KEY",
            azure_endpoint="gpt_4_o_mini_AZURE_OPENAI_ENDPOINT",
            deployment_name="gpt_4_o_mini_AZURE_OPENAI_DEPLOYMENT_NAME",
            api_version="gpt_4_o_mini_AZURE_OPENAI_API_VERSION",
            temperature=0.3
        )
        
    parse_chain = LLMChain(llm=gpt_4o_mini, prompt=parse_prompt)    
    tailored_cv = parse_chain.run({
    "cv_text": cv_text,
    "job_description": job_description
    })
    
    return tailored_cv

def generate_cover_letter(cv_text,job_description):
    parse_prompt = ChatPromptTemplate.from_messages([
    ("system", prom.cover_letter_prompt_system),
    ("human", prom.cover_letter_prompt_human)
    ])
    
    gpt_4o_mini = get_llm_model(
            openai_api_key="gpt_4_o_mini_AZURE_OPENAI_KEY",
            azure_endpoint="gpt_4_o_mini_AZURE_OPENAI_ENDPOINT",
            deployment_name="gpt_4_o_mini_AZURE_OPENAI_DEPLOYMENT_NAME",
            api_version="gpt_4_o_mini_AZURE_OPENAI_API_VERSION",
            temperature=0.3
        )
    
    parse_chain = LLMChain(llm=gpt_4o_mini, prompt=parse_prompt)    
    cover_letter = parse_chain.run({
    "cv_text": cv_text,
    "job_description": job_description
    })
    
    return cover_letter
