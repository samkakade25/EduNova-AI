# EduNova-AI

## To get started with the project:
1. Create a Python virtual environment:
    1. Create the virtual environment:
         python3 -m venv venvo
    2. Activate the virtual environment:
        source venv/bin/activate
    3. Install the requirements:
        pip install -r requirements.txt

    Replace database url : "mysql+pymysql://root:yourpassword@localhost:3306/invoices_db"
    Choose model : Groq Cloud API (llama3-8b-8192) 
                   Create a API key and replace

    Customize prompt according to your requirement and token size
    

###Command:

To run Backend:    [   uvicorn app:app --reload   ]

To run Frontend:   [    streamlit run web_ui.py   ]
