import spacy
import PyPDF2
import re
import json

nlp = spacy.load('en_core_web_sm')

# Open the PDF file in binary mode
with open('resume.pdf', 'rb') as pdf_file:
    # Create a PDF reader object
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)

    # Extract the text from each page of the PDF file
    text = ''
    for page_num in range(pdf_reader.getNumPages()):
        page = pdf_reader.getPage(page_num)
        text += page.extractText()

    # Clean up the text
    text = ' '.join(text.split())

    # Use Spacy to parse the text and extract relevant information
    doc = nlp(text)
    data = {}

    # Extract name
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

    # Extract skills
    skills = []
    for token in doc:
        if token.pos_ == 'NOUN' and token.dep_ == 'compound' and token.head.pos_ == 'NOUN' and token.head.dep_ == 'ROOT':
            skills.append(token.text)
    data['skills'] = skills if skills else None

    # Extract work experience
    experience = []
    exp_re = re.compile(r'\b([A-Z][a-z]+)\s(\d{4})\s-\s([A-Z][a-z]+)\s(\d{4})\b')
    matches = exp_re.findall(text)
    for match in matches:
        experience.append({
            'employer': match[0],
            'start_year': match[1],
            'end_year': match[3]
        })
    data['experience'] = experience if experience else None

    # Write the extracted information to a JSON file
    with open('resume_info.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

    # Print the extracted information
    print('Name:', name)
    print('Age:', age)
    print('Skills:', skills)
    print('Experience:', experience)
