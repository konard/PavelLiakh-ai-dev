import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from app.github_client import GitHubClient

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
client = OpenAI(api_key=OPENAI_API_KEY)

gh = GitHubClient()


def extract_code(text):
    code_blocks = re.findall(r"```(?:\w*\n)?(.*?)```", text, re.DOTALL)
    return "\n\n".join(code_blocks).strip() if code_blocks else text.strip()


def extract_target_file(issue_body):
    match = re.search(r"Target file\s*`(.+?)`", issue_body)
    return match.group(1) if match else None


def generate_code(issue_title, issue_body):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a senior developer. Respond exclusively with clean, production-ready code. "
                "Do not provide explanations or additional text. Adhere strictly to MCP standards, "
                "clearly separating system instructions from user requests."
            ),
        },
        {
            "role": "user",
            "content": (
                f"GitHub issue:\n"
                f"Title: {issue_title}\n"
                f"Description: {issue_body}\n\n"
                "Provide only the complete implementation code to solve this issue."
            ),
        },
    ]

    response = client.chat.completions.create(model=MODEL_NAME, messages=messages, temperature=0.0)

    raw_response = response.choices[0].message.content
    code = extract_code(raw_response)
    return code


def ask_model_for_filepath(issue_title, issue_body, generated_code, repo_file_paths):
    file_list = "\n".join(repo_file_paths[:100])
    prompt = (
        "You are helping decide where to place a newly generated piece of code.\n"
        "Below is a list of files in the repository:\n\n"
        f"{file_list}\n\n"
        f"Issue Title: {issue_title}\n"
        f"Issue Description: {issue_body}\n"
        f"Generated Code:\n{generated_code}\n\n"
        "From the file list above, suggest the most appropriate existing file path "
        "or propose a new one that fits the structure. Respond only with the path."
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )
    return response.choices[0].message.content.strip().split("\n")[0]


def determine_filepath(issue_number, issue_title, issue_body, generated_code):
    filepath = extract_target_file(issue_body)
    if not filepath:
        repo_file_paths = gh.get_repo_file_paths()
        print(repo_file_paths)
        filepath = ask_model_for_filepath(issue_title, issue_body, generated_code, repo_file_paths)
    if not filepath:
        filepath = f"generated/{issue_number}_auto_generated.py"
    return filepath


if __name__ == "__main__":
    issue_number = "1"
    issue_title = "Hello world code"
    issue_body = "Please provide me a simple Hello World code example in Python3.11"

    generated_code = generate_code(issue_title, issue_body)
    print(generated_code)
    filepath = determine_filepath(issue_number, issue_title, issue_body, generated_code)
    print(filepath)
