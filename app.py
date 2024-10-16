import os
import streamlit as st
import google.generativeai as genai
from typing import List, Dict, Any
from docx import Document
from dotenv import load_dotenv
import pypandoc
import anthropic
import openai
import tempfile

# Load environment variables
load_dotenv()

# Setup for different AI models
def setup_ai_model(model_name: str):
    if model_name == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        
        generation_config = {
            "temperature": 0,
            "max_output_tokens": 8192,
        }
        
        safety_settings = [
            {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        return genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
    elif model_name == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        return anthropic.Anthropic(api_key=api_key)
    elif model_name == "gpt4":
        api_key = os.getenv("OPENAI_API_KEY")
        return openai.OpenAI(api_key=api_key)
    else:
        raise ValueError(f"Unsupported model: {model_name}")

# Generate monthly status report
def generate_monthly_status_report(model_name: str, master_content: str, example_content: str) -> str:
    # Load the prompt from the file
    prompt = load_prompt("monthly_status_report")
    
    # Format the prompt with the variables
    formatted_prompt = prompt.format(
        master_content=master_content,
        example_content=example_content
    )
    
    model = setup_ai_model(model_name)
    
    try:
        if model_name == "gemini":
            response = model.generate_content(formatted_prompt, stream=True)
            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
            
            # Handling Safety Filters
            if response.candidates[0].finish_reason == "SAFETY":
                safety_ratings = response.candidates[0].safety_ratings
                safety_message = "Content was filtered due to safety concerns:\n"
                for rating in safety_ratings:
                    safety_message += f"- Category: {rating.category}, Probability: {rating.probability}\n"
                print(safety_message)
                return safety_message
            
            # Retrieving Usage Metadata
            if hasattr(response, 'usage_metadata'):
                prompt_tokens = response.usage_metadata.prompt_token_count
                candidates_tokens = response.usage_metadata.candidates_token_count
                print(f"Prompt tokens: {prompt_tokens}")
                print(f"Response tokens: {candidates_tokens}")
            
            return full_response
        
        elif model_name == "claude":
            response = model.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4096,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": formatted_prompt
                    }
                ]
            )
            return response.content[0].text
        
        elif model_name == "gpt4":
            response = model.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": formatted_prompt}],
                max_tokens=4096,
                temperature=0
            )
            return response.choices[0].message.content
        
    except Exception as e:
        error_message = f"An error occurred: {e}"
        print(error_message)
        return error_message

# File processing functions
def read_file(file):
    if file.name.endswith('.docx'):
        doc = Document(file)
        return '\n'.join([para.text for para in doc.paragraphs])
    elif file.name.endswith('.txt'):
        return file.getvalue().decode('utf-8')
    else:
        raise ValueError(f"Unsupported file type: {file.name}")

def process_input_files(files: List[Any]) -> Dict[str, str]:
    input_docs = {}
    for file in files:
        content = read_file(file)
        input_docs[file.name] = content
    return input_docs

# Prompt management functions
def load_prompt(prompt_name: str) -> str:
    prompt_folder = "./prompts"
    prompt_path = os.path.join(prompt_folder, f"{prompt_name}.txt")
    
    if os.path.exists(prompt_path):
        with open(prompt_path, 'r') as file:
            return file.read()
    else:
        raise FileNotFoundError(f"Prompt file '{prompt_name}.txt' not found in the prompts folder.")

# File saving and conversion functions
def save_markdown_to_file(markdown_content: str, file_path: str):
    with open(file_path, 'w') as md_file:
        md_file.write(markdown_content)

def convert_markdown_to_docx(markdown_file_path: str, output_file_path: str):
    pypandoc.convert_file(markdown_file_path, 'docx', outputfile=output_file_path)

# Streamlit app
def main():
    st.title("Monthly Status Report Generator")

    # File upload
    uploaded_files = st.file_uploader("Upload input files (Word or Text)", type=['docx', 'txt'], accept_multiple_files=True)

    if uploaded_files:
        # Process input files
        processed_docs = process_input_files(uploaded_files)

        # Combine documents into a master file
        master_content = "\n\n".join([f"File: {filename}\nContent: {content}" for filename, content in processed_docs.items()])

        # Read the example file (you might want to upload this separately or include it in your app)
        with open("./example/example.txt", 'r') as file:
            example_content = file.read()

        if st.button("Generate Report"):
            with st.spinner("Generating report..."):
                # Generate the monthly status report
                report = generate_monthly_status_report("gpt4", master_content, example_content)

                # Save the report as Word
                with tempfile.NamedTemporaryFile(delete=False, suffix='.md') as tmp_md:
                    save_markdown_to_file(report, tmp_md.name)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_docx:
                    convert_markdown_to_docx(tmp_md.name, tmp_docx.name)
                
                # Provide download link for Word report
                st.download_button(
                    label="Download Word Report",
                    data=open(tmp_docx.name, 'rb').read(),
                    file_name="monthly_status_report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

                # Display the generated report
                st.markdown(report)

                # Clean up temporary files
                os.unlink(tmp_md.name)
                os.unlink(tmp_docx.name)

if __name__ == "__main__":
    load_dotenv()
    main()
