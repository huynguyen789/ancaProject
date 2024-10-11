import os
import google.generativeai as genai
from typing import List, Dict
from docx import Document
from dotenv import load_dotenv
from IPython.display import Markdown, display
import pypandoc
import anthropic
import openai

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
def read_word_file(file_path: str) -> str:
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def process_input_docs(directory: str) -> Dict[str, str]:
    input_docs = {}
    for filename in os.listdir(directory):
        if filename.endswith('.docx'):
            file_path = os.path.join(directory, filename)
            content = read_word_file(file_path)
            input_docs[filename] = content
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

# Main execution
if __name__ == "__main__":

    # Process input documents
    input_directory = "./data_files/inputs/TO1_FFD_FederalFacilitiesDivision"
    processed_docs = process_input_docs(input_directory)

    # Export into a text file in the data_files/master_file folder
    os.makedirs("./data_files/master_file", exist_ok=True)
    output_file = "./data_files/master_file/master_file.txt"

    with open(output_file, 'w') as file:
        for filename, content in processed_docs.items():
            file.write(f"File: {filename}\n")
            file.write(f"Content: {content}\n")
            file.write("-" * 50 + "\n")
            file.write("\n\n")

    print(f"Combined documents exported to: {output_file}")

    # Read the master file and example file
    with open("./data_files/master_file/master_file.txt", 'r') as file:
        master_content = file.read()

    with open("./example/example.txt", 'r') as file:
        example_content = file.read()

    # Let user select the model
    model_choice = input("Choose a model (gemini/claude/gpt4): ").lower()
    while model_choice not in ["gemini", "claude", "gpt4"]:
        print("Invalid choice. Please choose gemini, claude, or gpt4.")
        model_choice = input("Choose a model (gemini/claude/gpt4): ").lower()

    # Generate the monthly status report in Markdown
    report = generate_monthly_status_report(model_choice, master_content, example_content)

    # Create outputs folder if it doesn't exist
    os.makedirs("./data_files/outputs", exist_ok=True)

    # Get the input folder name
    input_folder_name = os.path.basename(input_directory)

    # Save the Markdown report
    markdown_file = f"./data_files/outputs/{input_folder_name}_{model_choice}.md"
    save_markdown_to_file(report, markdown_file)

    # Convert the Markdown report to Word document
    docx_file = f"./data_files/outputs/{input_folder_name}_{model_choice}.docx"
    convert_markdown_to_docx(markdown_file, docx_file)

    print(f"Monthly Status Report has been generated using {model_choice} and saved to '{docx_file}'")

    # Display the generated report (if running in a Jupyter notebook)
    with open(markdown_file, 'r') as md_file:
        generated_report_content = md_file.read()
    display(Markdown(generated_report_content))