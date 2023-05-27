
setup:
    pip install -r requirements.txt

run:
    uvicorn api:app --reload
