* Prompt managements: save the
  prompts into ./prompt folder(create if not exits), then load from there.

GOOGLE GEMINI:

Using the Gemini API

This
documentation outlines how to set up and use the Gemini API based on the
provided code.

Setup

Import the necessary libraries:

```python



import
google.generativeai as genai



```

Configure the API with your key:

```python



api_key
= "YOUR_API_KEY_HERE"



genai.configure(api_key=api_key)



```

Creating a Model

Define the generation config:

```python



generation_config
= {



    "temperature": 0,



    "max_output_tokens": 8192,



}



```

Set up safety settings:

```python



safety_settings
= [



    {



        "category":
"HARM_CATEGORY_DANGEROUS",



        "threshold":
"BLOCK_NONE",



    },



    {



        "category":
"HARM_CATEGORY_HARASSMENT",



        "threshold":
"BLOCK_NONE",



    },



    {



        "category":
"HARM_CATEGORY_HATE_SPEECH",



        "threshold":
"BLOCK_NONE",



    },



    {



        "category":
"HARM_CATEGORY_SEXUALLY_EXPLICIT",



        "threshold":
"BLOCK_NONE",



    },



    {



        "category":
"HARM_CATEGORY_DANGEROUS_CONTENT",



        "threshold":
"BLOCK_NONE",



    }



]



```

Create the model:

```python



model
= genai.GenerativeModel(



    model_name="gemini-1.5-flash",



    generation_config=generation_config,



    system_instruction=system_instruction,



    safety_settings=safety_settings



)



```

Generating Content

To
generate content using the model:

```python



response
= model.generate_content(prompt, stream=True)



 



for
chunk in response:



    if chunk.candidates:



        candidate = chunk.candidates[0]



        if candidate.content and
candidate.content.parts:



            content =
candidate.content.parts[0].text



            # Process or display the content



```

Handling Safety Filters

The
code includes handling for safety filters:

```python



if
candidate.finish_reason == "SAFETY":



    safety_message = "\n\nNote: The
response was filtered due to safety concerns.\nSafety ratings:\n"



    for rating in candidate.safety_ratings:



        safety_message += f"- Category:
{rating.category}, Probability: {rating.probability}\n"



    # Process or display the safety message



```

Retrieving Usage Metadata

After
processing all chunks, you can retrieve usage metadata:

```python



if
hasattr(response, 'usage_metadata'):



    prompt_tokens =
response.usage_metadata.prompt_token_count



    candidates_tokens =
response.usage_metadata.candidates_token_count



    # Use these values as needed



```

Error Handling

The
code includes basic error handling:

```python



try:



    # API call and processing



except
Exception as e:



    error_message = f"An error occurred:
{e}"



    # Handle or display the error message



```

Remember
to replace `"YOUR_API_KEY_HERE"` with your actual Gemini API key and
adjust the `system_instruction` and other parameters as needed for your
specific use case.
