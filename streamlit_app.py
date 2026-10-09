
import streamlit as st
import requests

# FastAPI backend URL
API_URL = "http://127.0.0.1:8001/explain"

# Page configuration
st.set_page_config(
    page_title="GitHub Code Explainer",
    page_icon="💻",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
h1 {
    color: #243b64;
}
.stButton > button {
    background-color: #e65353;
    color: white;
    width: 100%;
    border-radius: 10px;
    height: 48px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# Header
st.title("💻 GitHub Code Explainer")
st.write("Understand any GitHub repository using local AI.")
st.divider()

# Information section
with st.container(border=True):
    st.subheader("🔍 How it works")
    st.write(
        "GitHub Repository → Code Processing → "
        "Local Qwen AI → Explanation"
    )
    st.write(
        "Enter a public GitHub repository URL. "
        "Our local Qwen model analyzes the source code "
        "and explains the project in simple English."
    )

# Input
st.subheader("🔗 Repository URL")

repo_url = st.text_input(
    "Enter your GitHub repository URL",
    placeholder="https://github.com/username/repository"
)

# Analyze repository
if st.button("🚀 Analyze Repository"):

    if not repo_url.strip():
        st.warning("Please enter a GitHub repository URL.")

    elif not repo_url.strip().startswith(
        "https://github.com/"
    ):
        st.error("Please enter a valid GitHub repository URL.")

    else:
        try:
            with st.spinner(
                "Analyzing repository with local Qwen AI..."
            ):
                response = requests.post(
                    API_URL,
                    json={"repo_url": repo_url.strip()},
                    timeout=600
                )

            if response.status_code == 200:
                data = response.json()

                if data.get("success"):
                    st.success("Analysis completed successfully!")

                    file_count = data.get(
                        "files_analyzed",
                        data.get("files_analyzed", 0)
                    )
                    st.metric("Files analyzed", file_count)

                    st.subheader("📘 Repository Explanation")
                    explanation = data.get("explanation", "")

                    if explanation:
                        st.markdown(explanation)
                    else:
                        st.warning("No explanation was returned.")
                else:
                    st.error(
                        data.get("detail", "Analysis failed.")
                    )

            else:
                try:
                    error = response.json().get(
                        "detail", response.text
                    )
                except ValueError:
                    error = response.text

                st.error(
                    f"Backend error ({response.status_code}): {error}"
                )

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to FastAPI. "
                "Start your backend on port 8001."
            )

        except requests.exceptions.Timeout:
            st.error(
                "The request timed out. Try a smaller repository."
            )

        except requests.exceptions.RequestException as exc:
            st.error(f"Request failed: {exc}")

st.divider()
st.caption("Powered by Streamlit • FastAPI • Ollama • Qwen2.5")
