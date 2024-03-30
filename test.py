import streamlit as st
import PyPDF2
import openai
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import re

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
        model="ft:gpt-3.5-turbo-0125:personal::98TxxR5J",  # You can use any appropriate GPT model here
        messages=[
            {"role": "system",
             "content": "Find all figures in group/consolidated section for the latest year that contains the word 'cash' and add them together ,  use group/consolidated, don't include cash in company, also DON'T DISPLAY prefix such as million or RM'000, and make sure to give me the sum if there are more than one cash related figures):"},
            {"role": "user", "content": text},
        ],
        max_tokens=4000,
    )
    total_cash = response['choices'][0]['message']['content'].strip()
    return total_cash

def extract_total_debt(text):

    response = openai.ChatCompletion.create(
        model="ft:gpt-3.5-turbo-0125:personal::98TxxR5J",  # You can use any appropriate GPT model here
        messages=[
            {"role": "system",
             "content": "Find all figures in group/consolidated section for the latest year that contains the word 'borrowing' and 'loan'(sum up short term and long term) and  add them together( please don't add any borrowings or loan under company! I only want group!,also don't take into account prefix such as million or RM'000) ):"},
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
        model="ft:gpt-3.5-turbo-0125:personal::98TxxR5J",  # You can use any appropriate GPT model here
        messages=[
            {"role": "system",
             "content": "Extract the total Asset for group/consolidated for the latest year from the provided text, also don't take into account prefix such as million or RM'000"},
            {"role": "user", "content": text},
        ],
        max_tokens=4000,
    )

    # Extracted text from OpenAI response
    extracted_text = response['choices'][0]['message']['content'].strip()
    return extracted_text

# def string_to_float(string):
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",  # You can use any appropriate GPT model here
#         messages=[
#             {"role": "system",
#              "content": "Extract the last figure in this String into a float as the return for this inquiry so that I can store it in a float variable. Please only return this in FLOAT ONLY! Help REMOVE comma if present!"},
#             {"role": "user", "content": string},
#         ],
#         max_tokens=4000,
#     )
#     floated = float((response['choices'][0]['message']['content'].strip()).replace(",",""))
#     return floated

def string_to_float(input_string):
    # Use regular expressions to find all floating-point numbers and integers
    new_string = input_string.replace(",", "").replace("RM", "")
    float_values = [float(value) for value in re.findall(r'\b\d+\.\d+\b', new_string)]
    int_values = [int(value) for value in re.findall(r'\b\d+\b', new_string)]

    # If float values are found, return the last float
    if float_values:
        return float_values[-1]
    # If no float values are found, but integers are found, return the last integer as float
    elif int_values:
        return float(int_values[-1])
    # If neither floats nor integers are found, return 0.0
    else:
        return 0.0

def is_shariah_compliant(coa, doa):
    syariah = coa < 33.0 and doa < 33.0
    if syariah:
        st.write("Congratulations! Your company is Shariah compliant.")
    else:
        st.write("Sorry, your company is not Shariah compliant.")

def calculate_coa(total_cash, total_asset):
    return (total_cash / total_asset) * 100

def calculate_doa(total_debt, total_asset):
    return (total_debt / total_asset) * 100

def is_shariah_compliant(coa, doa):
    return coa < 33.0 and doa < 33.0



def generate_ring_pie_chart(chart_name, percentage):
    # Ensure percentage is between 0 and 100
    percentage = max(0, min(100, percentage))

    # Calculate the remaining percentage
    remaining_percentage = 100.0 - percentage

    # Create figure
    fig = go.Figure(data=[go.Pie(labels=['COA', 'Remaining'], values=[percentage, remaining_percentage], hole=.3)])

    # Update layout
    fig.update_layout(title_text=chart_name)

    # Display the chart using Streamlit
    st.plotly_chart(fig)

def prefix_converter(text):
    response = openai.ChatCompletion.create(
        model="ft:gpt-3.5-turbo-0125:personal::98TxxR5J",  # You can use any appropriate GPT model here
        messages=[
            {"role": "system",
             "content": "please identify the prefix used in this financial report, etc million or RM'000, and convert it into float so that it can be used as a multiplier, I will store it as an float. If no multiplier is present, assign 1.0 ."},
            {"role": "user", "content": text},
        ],
        max_tokens=4000,
    )
    multiplier = response['choices'][0]['message']['content'].strip()
    numbers = re.findall(r'\b\d+(?:\.\d+)?\b', multiplier)

    # Convert numeric substrings to actual floats
    float_values = [float(num) for num in numbers]

    # If float values are found, return the last float
    if float_values:
        return float_values[-1]
    return multiplier




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
                        "Statements of financial position", "Statements of Financial Position",
"STATEMENTS OF FINANCIAL POSITION", "BALANCE SHEETS", "CONSOLIDATED STATEMENT OF FINANCIAL POSITION"]
            extracted_text = extract_pages_with_keywords(file_path, keywords)  # Pass file path instead of content

            multiplier = prefix_converter(extracted_text)
            st.write(multiplier)

            # Extract total assets using GPT
            total_assets_str = extract_total_assets(extracted_text)
            st.write(f" {total_assets_str}")

            total_cash_str = extract_total_cash(extracted_text)
            st.write(f" {total_cash_str}")

            total_debt_str = extract_total_debt(extracted_text)
            st.write(f" {total_debt_str}")

            total_assets = string_to_float(total_assets_str) * multiplier
            st.write("Total assets: RM" + str(total_assets))

            total_cash = string_to_float(total_cash_str) * multiplier
            st.write("Total cash: RM" + str(total_cash))

            total_debt = string_to_float(total_debt_str) * multiplier
            st.write("Total Debt: RM" + str(total_debt))

            COA = (total_cash / total_assets)*100
            DOA = (total_debt / total_assets)*100

            st.write("COA: {:.2f}%".format(COA))
            generate_ring_pie_chart("Cash over Asset Percentage Chart", COA)

            st.write("DOA: {:.2f}%".format(DOA))
            generate_ring_pie_chart("Debt over Asset Percentage Chart", DOA)

            syariah_compliant_1 = is_shariah_compliant(COA, DOA)
            if syariah_compliant_1:
                st.success("Congratulations! Your company is Syariah compliant.")
            else:
                st.error("Your company is not Syariah compliant.")

            submit_button = None  # Initialize submit_button

            if st.button("Appeal"):
                with st.form("input_form"):

                    total_asset_old = total_assets
                    total_cash_old = total_cash
                    total_debt_old = total_debt

                    st.write("Enter correct values if there are any errors:")
                    total_asset = st.number_input("Total Asset", value=total_asset_old)
                    total_debt = st.number_input("Total Debt", value=total_cash_old)
                    total_cash = st.number_input("Total Cash", value=total_debt_old)

                    submit_button = st.form_submit_button(label='Submit')

                if submit_button:
                    # Recalculate COA and DOA
                    COA = calculate_coa(total_cash, total_asset)
                    DOA = calculate_doa(total_debt, total_asset)

                    # Determine Syariah status
                syariah_compliant = is_shariah_compliant(COA, DOA)

                st.write("New Calculations:")
                st.write(f"COA: {COA:.2f}%")
                st.write(f"DOA: {DOA:.2f}%")
                if syariah_compliant:
                    st.success("Congratulations! Your company is Syariah compliant.")
                else:
                    st.error("Your company is not Syariah compliant.")



        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
