import google.generativeai as genai
import json
import os

def get_work_history() -> str:
    skill_string = read_history_files('work_history.json')

    print_skills(skill_string)

    return skill_string


def get_skills() -> str:
    skill_string = read_history_files('skills.json')

    print_skills(skill_string)

    return skill_string


def read_history_files(filename:str):
    full_path = './history_files/' + filename
    match filename:
        case 'skills.json':
            with open(full_path, 'r') as f:
                return build_skills_str(skills_dict=json.load(f))
        case 'work_history.json':
            pass


def build_skills_str(skills_dict:dict[str:str]) -> str:
    skills_str = ''
    for key_skill, years in skills_dict.items():
        skills_str += f'Skill: {key_skill}, with {years} year(s) of experience; '
    return skills_str


def print_skills(skills_str:str, hifen_amount=50) -> None:
    print(hifen_amount*'-')
    for skill in skills_str.split(';')[:-1]:
        print(skill, ';')
    print(hifen_amount*'-')


if __name__ == '__main__':
    # Check existence of API KEY
    load_api_key = os.environ.get("API_KEY", '')
    if not load_api_key:
        print('Insert your Gemini AI API KEY here:')
        api_key = input()
        os.environ.update(API_KEY=api_key)
        load_api_key = api_key
    genai.configure(api_key=load_api_key)

    skills_loaded_str =  get_skills()
    print('Considering this set of skills, tell me which job are you looking for?')
    job_title = input()

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f"Please, generate a curriculum for the job title {job_title} and with the following skills {skills_loaded_str}")
    print(response.text)