import streamlit as st
import requests
import json

# Set up the page
st.set_page_config(page_title="SAP Error Solution Assistant", page_icon="🤖")
st.title("SAP Error Solution Assistant 🤖")
st.markdown("Enter your SAP error details and Groq API key to get AI-powered solutions")

# Groq API configuration
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
SUPPORTED_MODELS = {
    "Llama 3 70B": "llama3-70b-8192",
    "Llama 3 8B": "llama3-8b-8192",
    "Mixtral 8x7B": "mixtral-8x7b-32768"  # Updated version if available
}

def get_groq_response(error_message, api_key, model):
    """Get SAP error solutions using Groq API with enhanced error handling"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [{
            "role": "system",
            "content": "You are an SAP technical expert providing error resolution guidance."
        }, {
            "role": "user",
            "content": f"Analyze this SAP error and provide solutions: {error_message}\n"
                       f"Structure response with:\n"
                       f"1. Error Analysis\n2. Immediate Steps\n"
                       f"3. Transaction Codes\n4. SAP Notes Reference\n"
                       f"5. Preventive Measures\nUse technical markdown formatting."
        }],
        "temperature": 0.3,
        "max_tokens": 1024,
        "top_p": 0.9
    }
    
    try:
        response = requests.post(GROQ_ENDPOINT, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error: {e.response.status_code}"
        if e.response.status_code == 400:
            try:
                error_data = e.response.json()
                error_msg += f"\nDetails: {error_data.get('error', {}).get('message', 'Unknown error')}"
            except json.JSONDecodeError:
                error_msg += "\nAdditional error details unavailable"
        st.error(error_msg)
        
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        
    return None

# API key input section with session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

api_key = st.text_input(
    "Enter your Groq API Key:",
    type="password",
    value=st.session_state.api_key,
    help="Get your API key from https://console.groq.com/",
    placeholder="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
)
st.session_state.api_key = api_key

# Model selection
selected_model = st.selectbox(
    "Choose AI Model:",
    options=list(SUPPORTED_MODELS.keys()),
    index=0,
    help="Llama 3 70B recommended for technical queries"
)

# User input section
with st.form("error_form"):
    error_input = st.text_area(
        "Enter SAP Error Message/Code:",
        placeholder="e.g., 'DBIF_RSQL_INVALID_RSQL' or 'Update termination error'",
        height=150,
        max_chars=2000
    )
    
    submitted = st.form_submit_button("Get Solutions")
    
    if submitted:
        cleaned_key = api_key.strip()
        
        if not cleaned_key:
            st.error("Please enter an API key")
        elif len(cleaned_key) < 20:
            st.error("Key appears too short. Valid Groq keys are 56 characters long")
        elif not cleaned_key.startswith("gsk_"):
            st.error("Invalid API key format. Valid Groq keys should:\n"
                     "- Start with 'gsk_'\n"
                     "- Be 56 characters long\n"
                     "- Contain only letters, numbers, and underscores")
        elif not error_input.strip():
            st.warning("Please enter an error message before submitting")
        else:
            with st.spinner(f"Analyzing error with {selected_model}..."):
                solution = get_groq_response(
                    error_input.strip(),
                    cleaned_key,
                    SUPPORTED_MODELS[selected_model]
                )
                
                if solution:
                    st.success("## Recommended Solutions")
                    st.markdown("---")
                    st.markdown(solution)
                    st.markdown("---")
                    st.info("**Verification Checklist:**\n"
                            "1. Test in development system first\n"
                            "2. Check SAP Notes\n"
                            "3. Consult system logs")
                else:
                    st.warning("No solutions generated. Possible fixes:\n"
                               "- Check API key validity\n"
                               "- Simplify error message\n"
                               "- Try different AI model")

# Model information sidebar
with st.sidebar:
    st.markdown("""
    **Supported Models:**
    - Llama 3 70B (Recommended)
      - 8192 token context
      - Best for technical queries
    - Llama 3 8B
      - Faster response times
      - Good for simple errors
    - Mixtral 8x7B
      - Expert mixture model
      - Multiple specialists approach

    **Current Limitations:**
    - Max 8192 tokens per request
    - Rate limits apply
    - Technical accuracy ~85%
    """)
    st.markdown("[Model Documentation](https://console.groq.com/docs/models)")

# Footer
st.markdown("---")
st.caption("⚠️ Always validate solutions with SAP documentation before implementation")