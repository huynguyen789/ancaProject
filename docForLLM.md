# Comprehensive LLM

Integration Documentation

## Table of Contents

1. [Streamlit
   Integration](#1-streamlit-integration)
2. [API
   Calls](#2-api-calls)
3. [Function
   Calling](#3-function-calling)
4. [Prompt
   Caching](#4-prompt-caching)
5. [Assistants
   API](#5-assistants-api)
6. [Best
   Practices](#6-best-practices)

## 1. Streamlit

Integration

### Session State

Management

Implement correct
session state management to prevent page resets on button clicks:

```python



if 'variable_name'
not in st.session_state:



    st.session_state.variable_name =
initial_value



 



# Access and update
session state



st.session_state.variable_name
= new_value



 



# Use st.rerun()
instead of experimental_rerun()



st.rerun()



```

### Streaming

Responses

For long-running
tasks, use streaming to display partial results:

```python



async def
stream_response(prompt):



    response = await
openai_client.chat.completions.create(



        model="gpt-4o",



        messages=[{"role":
"user", "content": prompt}],



        stream=True,



    )



  



    full_content = ""



    placeholder = st.empty()



    async for chunk in response:



        if chunk.choices[0].delta.content:



            full_content +=
chunk.choices[0].delta.content



            placeholder.markdown(full_content)



    return full_content



```

## 2. API Calls

### Anthropic

(Claude)

```python



from anthropic
import AsyncAnthropic



 



anthropic_client =
AsyncAnthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])



 



async def
get_anthropic_response(prompt):



    response = await
anthropic_client.messages.create(



     
model="claude-3-sonnet-20240229",  # Use Sonnet as default



        max_tokens=3000,



        temperature=0,



        messages=[



            {



                "role":
"user",



                "content": prompt



            }



        ]



    )



    return response.content[0].text



```

### OpenAI

```python



from openai import
AsyncOpenAI



 



openai_client =
AsyncOpenAI(api_key=st.secrets["OPENAI_API_KEY"])



 



async def
get_openai_response(prompt):



    response = await
openai_client.chat.completions.create(



        model="gpt-4o",  # Use GPT-4o as default



        messages=[



            {"role":
"system", "content": "You are a helpful
assistant."},



            {"role":
"user", "content": prompt}



        ],



        temperature=0



    )



    return response.choices[0].message.content



```

## 3. Function

Calling

Function calling
allows models to generate function arguments that adhere to provided
specifications.

### Defining

Functions

```python



tools = [



    {



        "type": "function",



        "function": {



            "name":
"get_current_weather",



            "description": "Get
the current weather",



            "parameters": {



                "type":
"object",



                "properties": {



                    "location": {



                        "type":
"string",



                     
"description": "The city and state, e.g. San Francisco,
CA",



                    },



                    "format": {



                        "type":
"string",



                        "enum":
["celsius", "fahrenheit"],



                     
"description": "The temperature unit to use. Infer this
from the users location.",



                    },



                },



                "required":
["location", "format"],



            },



        }



    },



    # Add more function definitions here



]



```

### Using Functions

```python



response =
client.chat.completions.create(



    model="gpt-4o",



    messages=messages,



    tools=tools,



    tool_choice="auto"  # Let the model decide when to use functions



)



 



# Check if the model
wants to call a function



if
response.choices[0].message.tool_calls:



    # Extract function call details and execute
the function



    tool_call =
response.choices[0].message.tool_calls[0]



    function_name = tool_call.function.name



    function_args =
json.loads(tool_call.function.arguments)



  



    # Execute the function and get the result



    function_response =
globals()[function_name](**function_args)



  



    # Add the function response to the
conversation



    messages.append({



        "role": "function",



        "name": function_name,



        "content": function_response



    })



```

## 4. Prompt Caching

OpenAI offers
discounted prompt caching for prompts exceeding 1024 tokens, resulting in up to
an 80% reduction in latency for longer prompts over 10,000 tokens.

### Key Features

- Automatically
  activates for prompts longer than 1024 tokens
- Caching is scoped
  at the organization level
- Eligible for zero
  data retention

### Checking Cached

Tokens

```python



response =
client.chat.completions.create(



    model="gpt-4o",



    messages=[...],



    # other parameters



)



 



cached_tokens =
response.usage.prompt_tokens_details.cached_tokens



print(f"Number
of cached tokens: {cached_tokens}")



```

### Best Practices

1. Place static or
   frequently reused content at the beginning of prompts
2. Maintain
   consistent usage patterns to prevent cache evictions
3. Monitor key
   metrics like cache hit rates, latency, and proportion of cached tokens

### Caching with

Tools and Multi-turn Conversations

- Ensure tool
  definitions and their order remain identical for caching
- Append new
  elements to the end of the messages array for multi-turn conversations

### Caching with

Images

- Images (linked or
  base64 encoded) qualify for caching
- Keep the `detail`
  parameter consistent for image tokenization
- GPT-4o models add
  extra tokens for image processing costs

## 5. Assistants API

The Assistants API
is a stateful evolution of the Chat Completions API, simplifying the creation
of assistant-like experiences and enabling access to tools like Code
Interpreter and Retrieval.

### Key Components

1. **Assistants**:
   Encapsulate a base model, instructions, tools, and context documents
2. **Threads**:
   Represent the state of a conversation
3. **Runs**: Power
   the execution of an Assistant on a Thread, including responses and tool use

### Creating an

Assistant

```python



assistant =
client.beta.assistants.create(



    name="Math Tutor",



    instructions="You are a personal math
tutor. Answer questions briefly, in a sentence or less.",



    model="gpt-4o",



    tools=[{"type":
"code_interpreter"}]



)



```

### Creating a

Thread and Run

```python



thread =
client.beta.threads.create()



 



message =
client.beta.threads.messages.create(



    thread_id=thread.id,



    role="user",



    content="I need to solve the equation
`3x + 11 = 14`. Can you help me?"



)



 



run =
client.beta.threads.runs.create(



    thread_id=thread.id,



    assistant_id=assistant.id



)



 



# Wait for the run
to complete



run =
wait_on_run(run, thread)



 



# Retrieve messages



messages =
client.beta.threads.messages.list(thread_id=thread.id)



```

## 6. Best Practices

- Use session state
  for maintaining app state in Streamlit

* When coding  a new app in the AI Assistant apps. Only
  focus on tha

- Implement
  streaming for long-running tasks to improve user experience
- Use asynchronous
  programming for efficient API calls
- Implement proper
  error handling for API calls and user inputs
- Place static
  content at the beginning of prompts for better cache efficiency
- Monitor caching
  metrics to optimize performance and cost-efficiency
- When using the
  Assistants API, leverage tools like Code Interpreter and Retrieval for enhanced
  capabilities
- For function
  calling, provide clear and specific function descriptions to guide the model's
  usage

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
