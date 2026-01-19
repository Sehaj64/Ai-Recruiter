# 🚀 AI Recruiter

An intelligent system for local resume analysis with a fast, API-powered chatbot, built with Streamlit and Google Gemini. This tool allows recruiters to quickly analyze multiple resumes against a job description, rank candidates based on skill overlap, and ask detailed questions about the candidate pool.

## ✨ Features

- **Bulk Resume Upload:** Upload multiple resumes in `.docx` or `.pdf` format.
- **Job Description Analysis:** Upload a job description to serve as the baseline for analysis.
- **Automated Candidate Ranking:** Automatically ranks candidates by calculating a "match percentage" based on the alignment of skills between the resume and the job description.
- **Detailed Candidate Profiles:** View extracted skills, experience, education, and project highlights for each candidate in an organized manner.
- **Conversational AI Chat:** Ask detailed, natural language questions about the candidates (e.g., "Who has more than 3 years of Python experience?" or "Compare the skills of candidate A and candidate B").
- **Secure API Key Handling:** Ensures that your Google Gemini API key is kept secure and is not exposed in the code.

## ☁️ Development in Codespaces

This repository is configured for development using [GitHub Codespaces](https://github.com/features/codespaces). This provides a complete, cloud-based development environment, ensuring you have the correct Python version and all dependencies ready to go.

To get started with Codespaces:

1.  Click the **"Code"** button on the repository's main page.
2.  Select the **"Codespaces"** tab.
3.  Click **"Create codespace on main"**.

GitHub will prepare the environment for you. The `postCreateCommand` in the `.devcontainer/devcontainer.json` configuration will automatically run, installing all Python packages from `requirements.txt` and downloading the necessary spaCy model.

### Adding Your API Key in Codespaces

You must add your Gemini API key as a secret to your Codespace for the application to work.

1.  Once the Codespace is running, find the `.streamlit` directory.
2.  Create a new file named `secrets.toml` inside the `.streamlit` directory.
3.  Add the following content to the file, replacing `YOUR_API_KEY_GOES_HERE` with your actual key:
    ```toml
    GEMINI_API_KEY = "YOUR_API_KEY_GOES_HERE"
    ```
This method ensures your key is kept secure within your Codespace environment.

## 🛠️ Local Setup and Installation

Follow these steps to get the AI Recruitor running on your local machine.

### Prerequisites

- Python 3.8+
- A Google Gemini API Key. You can get one for free from [Google AI Studio](https://aistudio.google.com/app/apikey).

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Sehaj64/Ai-Recruitor.git
    cd Ai-Recruitor
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    You will also need to download the `spacy` model for English:
    ```bash
    python -m spacy download en_core_web_sm
    ```

4.  **Set up your API Key:**
    - Navigate to the `.streamlit` directory.
    - **Create a copy** of the `secrets.toml.template` file and **rename it** to `secrets.toml`.
    - Open the `secrets.toml` file and replace `"YOUR_TOKEN_HERE"` with your actual Google Gemini API key.

    ```toml
    # .streamlit/secrets.toml

    GEMINI_API_KEY = "YOUR_API_KEY_GOES_HERE"
    ```

## 🏃‍♀️ Usage

Once the setup is complete, you can run the application with the following command:

```bash
streamlit run /workspaces/IPL-Auction-Strategy/app.py
```

The application will open in your web browser.

1.  **Upload a Job Description:** Use the file uploader in the sidebar to upload the job description file.
2.  **Upload Resumes:** Upload one or more candidate resumes.
3.  **Analyze:** Click the "Analyze Candidates" button.
4.  **View Results:** The main panel will display a ranked table of candidates. You can expand each candidate's profile to see more details.
5.  **Chat:** Use the chat input at the bottom to ask questions about the analyzed documents.

---

*This project is for demonstration purposes and is licensed under a Source-Available (View Only) license. See the `LICENSE` file for more details.*

## ?? Cloud Deployment (CI/CD)

This project includes a fully automated MLOps pipeline:

- **Containerization:** Docker
- **Registry:** AWS Elastic Container Registry (ECR)
- **Orchestration:** AWS App Runner
- **Automation:** GitHub Actions

Every push to the \main\ branch automatically builds the Docker image and pushes it to AWS for zero-downtime deployment.
