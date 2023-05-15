from flask import Flask, render_template, request, jsonify
import spacy
import fitz
import re
import json

app = Flask(__name__)

nlp = spacy.load('en_core_web_sm')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Get the uploaded file from the request
    file = request.files['resume']

    # Check if the uploaded file is a PDF file
    if file and file.filename.split('.')[-1].lower() == 'pdf':
        # Open the PDF file in binary mode
        with fitz.open(stream=file.read(), filetype='pdf') as pdf_file:
            # Extracting the text from each page of the PDF file
            text = ''
            for page in pdf_file:
                text += page.get_text()

            # Cleaning  up the text
            text = ' '.join(text.split())

            # Using  Spacy to parse the text and extract relevant information
            doc = nlp(text)
            data = {}

            # Extracting the  name of the individual 
            name = ''
            for ent in doc.ents:
                if ent.label_ == 'PERSON':
                    name = ent.text
                    break
            data['name'] = name if name else None

            # Extract age
            age = ''
            age_re = re.compile(r'\b\d{1,2}\b\s*(years old|yo|Y\.O\.|yrs|years)')
            match = age_re.search(text)
            if match:
                age = match.group(0)
            data['age'] = age if age else None

            # Extracting  contact information
            contact = {}
            email_re = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
            phone_re = re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b')
            address_re = re.compile(r'\b\d+\s+([A-Za-z]+\s+){1,3}(St\.|Ave\.|Rd\.|Blvd\.|Ln\.)\b')
            for token in doc:
                if token.like_email:
                    match = email_re.search(token.text)
                    if match:
                        contact['email'] = match.group(0)
                elif phone_re.search(token.text):
                    match = phone_re.search(token.text)
                    if match:
                        contact['phone'] = match.group(0)
                elif token.is_stop and token.nbor().is_title:
                    match = address_re.search(f'{token.text} {token.nbor().text}')
                    if match:
                        contact['address'] = match.group(0)
            data['contact'] = contact if contact else None

            # Converting the extracted information into a JSON response
            response = jsonify(data)
            response.status_code = 200
            return response

    else:
        # If the uploaded file is not a PDF, return an error response
        error = {'error': 'The uploaded file is not a PDF file.'}
        response = jsonify(error)
        response.status_code = 400
        return response

if __name__ == '__main__':
    app.run(debug=True)
