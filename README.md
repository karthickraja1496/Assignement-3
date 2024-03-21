# Assignement3
BizCardX is a Python-based tool designed to simplify the extraction of data from business cards using Optical Character Recognition (OCR). This project streamlines the process of digitizing business card information, making it efficient and user-friendly.

# Project Overview
BizCardX aims to simplify the process of extracting and managing information from business cards. The tool offers the following features:

Extraction of key information from business cards: company name, cardholder name, designation, contact details, etc.
Storage of extracted data in a MySQL database for easy access and retrieval.
GUI built with Streamlit for a user-friendly interface.
User options to upload, extract, and modify business card data.

# Features
OCR Extraction: Utilizes Optical Character Recognition to extract text data from business card images.

Output Organization: Provides a structured and organized output format for the extracted information.

Image Format Support: Supports various image formats commonly used for business cards.

# Workflow
Install the required libraries using the command pip install [Name of the library]. Install streamlit, mysql.connector, pandas, and easyocr.
Execute the BizCardX_main.py script using the command streamlit run BizCardX_main.py.
The web application opens in a browser, presenting the user with three menu options: HOME, UPLOAD & EXTRACT, MODIFY.
Users can upload a business card image in the UPLOAD & EXTRACT menu.
The EasyOCR library extracts text from the uploaded image.
Extracted text is classified using regular expressions to identify key information such as company name, cardholder name, etc.
The classified data is displayed on the screen and can be edited by the user if needed.
Clicking the "Upload to Database" button stores the data in a MySQL database.
The MODIFY menu allows users to read, update, and delete data in the MySQL database.
