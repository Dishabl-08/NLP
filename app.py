import streamlit as st
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from google.api_core import exceptions

# Load environment variables
load_dotenv()

# Configure Gemini API with error handling
def configure_gemini():
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            st.error("❌ GEMINI_API_KEY not found in environment variables. Please check your .env file.")
            st.stop()
        
        genai.configure(api_key=api_key)
        
        # Test the API key by making a simple request
        try:
            model = genai.GenerativeModel('gemini-pro')
            # Make a simple test request
            _ = model.generate_content("Test")
            return model
        except exceptions.InvalidArgument as e:
            st.error("❌ Invalid API key. Please check your GEMINI_API_KEY in the .env file.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Error initializing Gemini model: {str(e)}")
            st.stop()
    except Exception as e:
        st.error(f"❌ Configuration error: {str(e)}")
        st.stop()

# Load company data
def load_company_data():
    return {
        "policies": {
            "work_hours": "Meta operates on flexible work hours with core collaboration hours from 10 AM to 4 PM local time.",
            "remote_work": "Meta offers hybrid work options with a minimum of 3 days in office per week.",
            "code_of_conduct": "Meta employees must adhere to our community standards and ethical guidelines.",
            "security": "All employees must use two-factor authentication and follow security protocols.",
            "benefits": "Comprehensive health insurance, 401(k) matching, RSUs, and wellness programs.",
        },
        "roles": {
            "software_engineer": {
                "responsibilities": "Develop and maintain Meta's products and infrastructure",
                "tools": "Internal development tools, Git, Meta's testing frameworks",
                "team_structure": "Agile teams with daily standups and bi-weekly sprints"
            },
            "product_manager": {
                "responsibilities": "Drive product strategy and execution",
                "tools": "Product analytics tools, roadmap planning software",
                "team_structure": "Cross-functional teams with engineers and designers"
            },
            "data_scientist": {
                "responsibilities": "Analyze user behavior and product metrics",
                "tools": "Internal analytics platforms, Python, SQL",
                "team_structure": "Embedded in product teams with regular stakeholder reviews"
            }
        },
        "faqs": {
            "first_day": "You'll attend orientation, set up your workstation, and meet your team.",
            "it_support": "Contact IT Help Desk through workplace portal or email it@meta.com",
            "parking": "Free parking available at all Meta offices with registered vehicle",
            "dress_code": "Casual dress code - be comfortable and professional",
            "lunch": "Free meals provided at all Meta cafeterias"
        }
    }

def generate_response(model, query, context):
    try:
        prompt = f"""
        You are Meta's AI onboarding assistant. Using the following company information, 
        provide a helpful and friendly response to the query. Stay strictly within the 
        provided context and if information isn't available, kindly say so.

        Context:
        {context}

        Query: {query}

        Provide a conversational, helpful response focusing only on relevant information.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except exceptions.InvalidArgument as e:
        st.error("❌ API Error: Invalid API key or request. Please check your configuration.")
        return None
    except Exception as e:
        st.error(f"❌ Error generating response: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Meta Onboarding Assistant",
        page_icon="🤖",
        layout="wide"
    )

    st.title("🤖 Meta Employee Onboarding Assistant")
    st.write("Welcome! I'm here to help you learn about Meta's policies, roles, and answer your questions.")

    # Check if API key exists before proceeding
    if not os.getenv('GEMINI_API_KEY'):
        st.error("❌ Please set up your GEMINI_API_KEY in the .env file")
        st.code("""
        1. Create a .env file in your project directory
        2. Add the following line:
        GEMINI_API_KEY=your-api-key-here
        3. Replace 'your-api-key-here' with your actual Gemini API key
        """)
        st.stop()

    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Initialize Gemini
    model = configure_gemini()

    # Only proceed if model is properly initialized
    if model:
        company_data = load_company_data()

        # Add role selector
        role = st.sidebar.selectbox(
            "Select your role:",
            ["software_engineer", "product_manager", "data_scientist"]
        )

        # Display relevant role information
        with st.sidebar:
            st.write("### Your Role Information")
            role_info = company_data["roles"][role]
            for key, value in role_info.items():
                st.write(f"**{key.title()}:** {value}")

        # Chat interface
        user_input = st.text_input("Ask me anything about Meta's policies, your role, or general questions:")
        
        if st.button("Send"):
            if user_input:
                # Prepare context based on query
                context = json.dumps({
                    "policies": company_data["policies"],
                    "role_info": company_data["roles"][role],
                    "faqs": company_data["faqs"]
                })
                
                # Get response
                response = generate_response(model, user_input, context)
                
                if response:
                    # Add to chat history
                    st.session_state.chat_history.append(("user", user_input))
                    st.session_state.chat_history.append(("assistant", response))

        # Display chat history
        for role, message in st.session_state.chat_history:
            if role == "user":
                st.write("You:", message)
            else:
                st.write("Assistant:", message)

if __name__ == "__main__":
    main()