import streamlit as st
import PyPDF2
import openai
import os

# Set your OpenAI API key
openai.api_key = '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'

def save_uploaded_file(uploaded_file, folder_path, file_name):
    # Create the uploads directory if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)
    # Save the file to the uploads directory
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# def extract_pages_with_keywords(input_pdf_path, keywords):
#     # Open the PDF file
#     with open(input_pdf_path, "rb") as file:
#         # Create a PdfReader object
#         pdf_reader = PyPDF2.PdfReader(file)
#         # Initialize an empty string to store the extracted pages
#         extracted_pages_text = ""
#
#         # Iterate through each page of the PDF
#         for page_number, page in enumerate(pdf_reader.pages, start=1):
#             # Extract text from the page
#             page_text = page.extract_text()
#             # Check if any of the keywords are present in the page text
#             if any(keyword in page_text for keyword in keywords):
#                 # Append the page text to the extracted pages string
#                 extracted_pages_text += page_text
#
#         return extracted_pages_text

def extract_pages_with_keywords(pdf_file, keywords):
    # Create a PdfReader object directly from the file object
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    # Initialize an empty string to store the extracted pages
    extracted_pages_text = ""

    # Iterate through each page of the PDF
    for page_number, page in enumerate(pdf_reader.pages, start=1):
        # Extract text from the page
        page_text = page.extract_text()
        # Check if any of the keywords are present in the page text
        if any(keyword in page_text for keyword in keywords):
            # Append the page text to the extracted pages string
            extracted_pages_text += page_text

    return extracted_pages_text


def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        # Extract text from each page
        page_text = page.extract_text()
        # Concatenate text from non-consolidated pages
        text += page_text.strip() + " "
    return text.strip()

def syariah_test_passed(cash_over_asset, debt_over_asset):
    return cash_over_asset < 33 and debt_over_asset < 33

def extract_total_cash(text):

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # You can use any appropriate GPT model here
        messages=[
            {"role": "system",
             "content": "Find all figures in group/consolidated section for the latest year that contains the word 'cash' and add them together ):"},
            {"role": "user", "content": text},
        ],
        max_tokens=4000,
    )
    total_cash = response['choices'][0]['message']['content'].strip()
    return total_cash

def extract_total_debt(text):

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # You can use any appropriate GPT model here
        messages=[
            {"role": "system",
             "content": "Find all figures in group/consolidated section for the latest year that contains the word 'borrowing' and 'loan' and  add them together( please don't add any borrowings or loan under company! I only want group!) ):"},
            {"role": "user", "content": text},
        ],
        max_tokens=4000,
    )
    total_debt = response['choices'][0]['message']['content'].strip()
    return total_debt

def extract_total_assets(text):
    # Use GPT to extract total assets from the text
    # Extract financial ratios using GPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # You can use any appropriate GPT model here
        messages=[
            {"role": "system",
             "content": "Extract the total Asset for group/consolidated for the latest year from the provided text(don't bullshit I want only the unit and the number ):"},
            {"role": "user", "content": text},
        ],
        max_tokens=4000,
    )

    # Extracted text from OpenAI response
    extracted_text = response['choices'][0]['message']['content'].strip()
    return extracted_text

def string_to_float(string):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # You can use any appropriate GPT model here
        messages=[
            {"role": "system",
             "content": "Extract the last figure in this String into a float as the return for this inquiry so that I can store it in a float variable. Please only return this in FLOAT ONLY! Help REMOVE comma if present!"},
            {"role": "user", "content": string},
        ],
        max_tokens=4000,
    )
    floated = float((response['choices'][0]['message']['content'].strip()).replace(",",""))
    return floated

def main():
    st.title("Syariah Compliance Checker")
    st.write("Upload a PDF file and we will determine if your company is Syariah-Compliant.")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        try:
            # Save the uploaded file to the uploads directory with the name "stored.pdf"
            uploads_dir = "uploads"
            file_path = save_uploaded_file(uploaded_file, uploads_dir, "stored.pdf")

            keywords = ["STATEMENTS OF FINANCIAL POSITION", "STATEMENT OF FINANCIAL POSITION",
                        "Statements of financial position", "STATEMENTS OF FINANCIAL POSITION", "BALANCE SHEETS"]
            extracted_text = extract_pages_with_keywords(file_path, keywords)  # Pass file path instead of content

            # Extract total assets using GPT
            total_assets_str = extract_total_assets(extracted_text)
            # st.write(f" {total_assets_str}")

            total_cash_str = extract_total_cash(extracted_text)
            # st.write(f" {total_cash_str}")

            total_debt_str = extract_total_debt(extracted_text)
            # st.write(f" {total_debt_str}")

            total_assets = string_to_float(total_assets_str)
            st.write("Total assets: " + str(total_assets))

            total_cash = string_to_float(total_cash_str)
            st.write("Total cash: " + str(total_cash))

            total_debt = string_to_float(total_debt_str)
            st.write("Total Debt: " + str(total_debt))

            COA = total_cash / total_assets
            DOA = total_debt / total_assets

            st.write("COA: " + str(COA))
            st.write("DOA: " + str(DOA))

        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
