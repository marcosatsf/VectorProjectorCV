import argparse
import configparser
from datetime import datetime
import google.generativeai as genai
import json
import os

PREFIX_PATH = './history_files/'
config = configparser.ConfigParser()
config.read('config.ini')

def print_infos(f):
    hifen_amount = 50
    def new_print(*args, **kwargs):
        print(hifen_amount*'-')
        f(*args, **kwargs)
        print(hifen_amount*'-')

    return new_print


def get_work_history() -> str:
    work_string = read_history_files('work_history.json')

    print(work_string)

    return work_string


def get_education_history() -> str:
    work_string = read_history_files('education_history.json')

    print(work_string)

    return work_string


def get_skills() -> str:
    skill_string = read_history_files('skills.json')

    print_skills(skill_string)

    return skill_string


def read_history_files(filename:str):
    full_path = PREFIX_PATH + filename
    match filename:
        case 'skills.json':
            with open(full_path, 'r') as f:
                return build_skills_str(skills_dict=json.load(f))
        case 'work_history.json':
            with open(full_path, 'r') as f:
                return build_work_str(works_list=json.load(f)["job_list"], prefix_load=PREFIX_PATH)


def build_skills_str(skills_dict:dict[str:str]) -> str:
    skills_str = ''
    for key_skill, years in skills_dict.items():
        skills_str += f'Skill: {key_skill}, with {years} year(s) of experience; '
    return skills_str


def build_work_str(works_list:list, prefix_load:str='') -> str:
    work_str = ''
    description_doc_list = []
    for work_obj in works_list:
        # If needs to load job description
        if not work_obj['description']:
            # If needs to load the description document. It should load once by run
            if not description_doc_list:
                with open(f'{prefix_load}job_description.txt', 'r') as f:
                    # Parse it
                    description_doc_list = f.read().splitlines()
            # Attribute to the correct job_description id
            curr_idx = description_doc_list.index(f'[job_id={work_obj['id_description']}]')
            try:
                next_idx = description_doc_list[curr_idx:].index('[job_id=')
            except ValueError:
                next_idx = len(description_doc_list)
            work_obj['description'] = '\n'.join(description_doc_list[curr_idx+1:next_idx])
        work_str += f"""
Job title is {work_obj['job title']} at {work_obj['company name']}.
Starting from {work_obj['from']} to {work_obj['to']}. {work_obj['description']}\n\n"""

    return work_str


@print_infos
def print_skills(skills_str:str) -> None:
    for skill in skills_str.split(';')[:-1]:
        print(skill, ';', sep='')


def post_generation_format(text:str) -> str:
    contact_info = f"""
{os.environ.get('Name','')}
Phone: {os.environ.get('Phone','')}
Email: {os.environ.get('Email','')}
LinkedIn: {os.environ.get('LinkedIn','')}
GitHub: {os.environ.get('GitHub','')}
"""
    text_splitted = text.split('\n')
    extra_sections = ['Contact Information:', 'Education', 'Projects', 'Awards and Recognition']
    for sec in extra_sections:
        try:
            section_index = text_splitted.index(f'**{sec}**')
            if sec == 'Contact Information:':
                del text_splitted[section_index]
                text_splitted.insert(1, contact_info)
            else:
                with open(f'{PREFIX_PATH}{sec.split(' ')[0].lower()}_history.txt', 'r') as f:
                    text_splitted[section_index+2] = f.read()
        except ValueError:
            pass
        except OSError:
            #Deletes whole section 😅
            del text_splitted[section_index:section_index+4]
    text = '\n'.join(text_splitted)
    return text


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="VectorProjectorCV",
        description='Project your skill vector to different kind of job titles'
    )
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()


    # Check existence of API KEY
    load_api_key = os.environ.get("API_KEY", '')
    if not load_api_key:
        print('Insert your Gemini AI API KEY here:')
        api_key = input()
        os.environ.update(API_KEY=api_key)
        load_api_key = api_key
    genai.configure(api_key=load_api_key)

    # Load work and skills
    work_loaded_str = get_work_history()
    skills_loaded_str =  get_skills()
    print('Considering this set of skills, tell me which job are you looking for?')
    job_title = input()

    if not args.debug:
        # Instantiate model obj and make the call
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Generate a curriculum for the job title {job_title}. With the following skills {skills_loaded_str} and the next background experience {work_loaded_str}")
        text_formatted = post_generation_format(response.text)
        print(text_formatted)
        with open(f'./output/generated_cv_{datetime.now().timestamp()}.txt', 'w') as f:
            f.write(text_formatted)