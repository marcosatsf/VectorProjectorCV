# VectorProjectorCV
Project your skill vector to different kind of job titles

## Description
Considering we're all vectors of N dimensions. Each dimension is a skill with a given intensity, based on the years of experience.
With that said, this project aims to project this vector to a given job title, in order to best match it!*

## How-to
Remove suffix `_example` from `history_files_example` and edit files inside it accordingly.
Run:
```
pipenv install -r requirements.txt
pipenv run vector_projector.py
```

### Caveats

*This project uses GeminiAI_API, be ready to yourself one API_KEY and put it at the first you run this script! Or just add it into `.env` file like ```API_KEY='<API_KEY_VALUE>'```
