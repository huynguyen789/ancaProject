import os
from docx import Document
from typing import List, Dict

def read_word_file(file_path: str) -> str:
    """
    Read the content of a Word file.
    
    Args:
    file_path (str): Path to the Word file
    
    Returns:
    str: Content of the Word file
    """
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def process_input_docs(directory: str) -> Dict[str, str]:
    """
    Process all Word files in the given directory.
    
    Args:
    directory (str): Path to the directory containing Word files
    
    Returns:
    Dict[str, str]: A dictionary with filenames as keys and file contents as values
    """
    input_docs = {}
    for filename in os.listdir(directory):
        if filename.endswith('.docx'):
            file_path = os.path.join(directory, filename)
            content = read_word_file(file_path)
            input_docs[filename] = content
    return input_docs

# Example usage
if __name__ == "__main__":
    input_directory = "./example"   #"./data_files/inputs"
    
    processed_docs = process_input_docs(input_directory)
    
    # Export into a text file in the data_files/master_file folder
    os.makedirs("./data_files/master_file", exist_ok=True)
    output_file = "./data_files/master_file/master_file.txt"
    
    with open(output_file, 'w') as file:
        for filename, content in processed_docs.items():
            file.write(f"File: {filename}\n")
            file.write(f"Content: {content}\n")
            file.write("-" * 50 + "\n")
            file.write("\n\n")x
    
    print(f"Combined documents exported to: {output_file}")
    
    # Print the results
    for filename, content in processed_docs.items():
        print(f"File: {filename}")
        print(f"Content: {content}")
        print("-" * 50)
        print("\n\n")