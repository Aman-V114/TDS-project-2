import httpx
import os
import json

from utils.function_definations_llm import function_definitions_objects_llm

# OpenAI API settings
openai_api_chat = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
openai_api_key = os.getenv("AIPROXY_TOKEN")

headers = {
    "Authorization": f"Bearer {openai_api_key}",
    "Content-Type": "application/json",
}


def extract_parameters(prompt: str, function_definitions_llm):
    """Send a user query to OpenAI API and extract structured parameters."""
    try:
        # Print debug information
        print(f"Extracting parameters for prompt: {prompt}")
        print(f"Function definition: {function_definitions_llm}")
        
        # Make sure we have a valid API key
        if not openai_api_key:
            print("Error: AIPROXY_TOKEN environment variable not set")
            return {"name": function_definitions_llm.get("name", "default"), "arguments": "{}"}
        
        with httpx.Client(timeout=20) as client:
            # Construct a better API request
            response = client.post(
                openai_api_chat,
                headers=headers,
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are an intelligent assistant that extracts parameters from user queries. For image compression requests, always include an image_path parameter."},
                        {"role": "user", "content": prompt}
                    ],
                    "tools": [
                        {
                            "type": "function", 
                            "function": function_definitions_llm  # Pass the definition directly
                        }
                    ],
                    "tool_choice": {"type": "function", "function": {"name": function_definitions_llm.get("name")}}
                },
            )
        
        response.raise_for_status() 
        response_data = response.json()
        
        # Print full response for debugging
        print(f"API Response: {response_data}")
        
        if "choices" in response_data and response_data["choices"] and "message" in response_data["choices"][0]:
            message = response_data["choices"][0]["message"]
            
            if "tool_calls" in message and message["tool_calls"]:
                extracted_data = message["tool_calls"][0]["function"]
                return extracted_data
            else:
                # If no tool_calls, create a default parameters structure
                return {
                    "name": function_definitions_llm.get("name", "default"),
                    "arguments": json.dumps({"image_path": "tmp_uploads/images/default.jpg"})
                }
        else:
            print("No valid choices in response")
            return {
                "name": function_definitions_llm.get("name", "default"),
                "arguments": json.dumps({"image_path": "tmp_uploads/images/default.jpg"})
            }
    except httpx.RequestError as e:
        print(f"Request error: {e}")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    # Return default parameters if any exception occurs
    return {
        "name": function_definitions_llm.get("name", "default"),
        "arguments": json.dumps({"image_path": "tmp_uploads/images/default.jpg"})
    }


# Example usage
queries = [
    "Send a HTTPS request to https://httpbin.org/get with the URL encoded parameter email set to 23f2005217@ds.study.iitm.ac.in",
    # "Run npx -y prettier@3.4.2 README.md | sha256sum.",
    # "Type this formula in Google Sheets: =SUM(ARRAY_CONSTRAIN(SEQUENCE(100, 100, 15, 12), 1, 10))",
]

function_defs = [
    "make_http_requests_with_uv",
    # "run_command_with_npx",
    # "use_google_sheets",
]

for i in range(len(queries)):
    result = extract_parameters(queries[i], function_definitions_objects_llm[function_defs[i]])
    # print(function_definitions_objects_llm[function_defs[i]])
    print(result)
