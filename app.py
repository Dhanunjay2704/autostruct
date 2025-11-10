import streamlit as st
import os
import json
import yaml
import re
import shutil
import tempfile
from pathlib import Path

# Page config
st.set_page_config(
    page_title="AutoStruct - Project Structure Generator",
    page_icon="🏗️",
    layout="wide"
)

# Title and description
st.title("🏗️ AutoStruct")
st.subheader("Smart Project Folder/File Structure Generator")

st.markdown("Create project structures instantly from ASCII, JSON, or YAML input!")

# -----------------------------
# Parsing Functions
# -----------------------------
def parse_ascii(text):
    """Parse ASCII tree format into dictionary structure"""
    lines = text.strip().split('\n')
    result = {}
    stack = [(result, -1)]
    
    for line in lines:
        if not line.strip():
            continue
        
        indent = 0
        content_start = 0
        for i, char in enumerate(line):
            if char in ' \t│':
                indent += 1
            elif char in '├└┌┐┘┬┴┼─':
                content_start = i + 1
                while content_start < len(line) and line[content_start] in ' ─':
                    content_start += 1
                    indent += 1
                break
            else:
                content_start = i
                break
        
        cleaned = line[content_start:].strip() if content_start < len(line) else line.strip()
        cleaned = re.sub(r'^[├└│─┌┐┘┬┴┼\s]*', '', cleaned)
        cleaned = re.sub(r'[├└│─┌┐┘┬┴┼]+\s*', '', cleaned).strip()
        cleaned = re.sub(r'^[\s─]+', '', cleaned)
        cleaned = re.sub(r'[\s─]+$', '', cleaned)
        
        if not cleaned:
            continue
        
        while len(stack) > 1 and stack[-1][1] >= indent:
            stack.pop()
        
        current_dict = stack[-1][0]
        
        if cleaned.endswith('/'):
            folder_name = cleaned[:-1]
            if folder_name:
                current_dict[folder_name] = {}
                stack.append((current_dict[folder_name], indent))
        else:
            current_dict[cleaned] = None
    return result

def parse_json(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON format: {e}")
        return None

def parse_yaml(text):
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as e:
        st.error(f"Invalid YAML format: {e}")
        return None

# -----------------------------
# Validation & Creation
# -----------------------------
def validate_structure(structure):
    issues = []
    def validate_recursive(obj, current_path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if re.search(r'[<>:"|?*]', key):
                    issues.append(f"Invalid characters in name: {current_path}/{key}")
                new_path = f"{current_path}/{key}" if current_path else key
                if isinstance(value, dict):
                    validate_recursive(value, new_path)
    validate_recursive(structure)
    return issues

def create_structure(structure, base_path, dry_run=False):
    logs = []
    def create_recursive(obj, current_path):
        if not isinstance(obj, dict):
            return
        for key, value in obj.items():
            full_path = os.path.join(current_path, key)
            try:
                if value is None:
                    if not dry_run:
                        os.makedirs(os.path.dirname(full_path), exist_ok=True)
                        with open(full_path, 'w') as f:
                            pass
                    logs.append(f"✅ {'[DRY RUN] ' if dry_run else ''}Created file: {full_path}")
                elif isinstance(value, dict):
                    if not dry_run:
                        os.makedirs(full_path, exist_ok=True)
                    logs.append(f"📁 {'[DRY RUN] ' if dry_run else ''}Created folder: {full_path}")
                    create_recursive(value, full_path)
            except Exception as e:
                logs.append(f"❌ Error creating {full_path}: {str(e)}")
    if isinstance(structure, dict):
        create_recursive(structure, base_path)
    return logs

# -----------------------------
# UI Layout
# -----------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Input Structure")
    input_method = st.radio("Choose input method:", ["Paste Text", "Upload File"])
    structure_text = ""
    if input_method == "Paste Text":
        structure_text = st.text_area(
            "Paste your structure here:",
            height=300,
            placeholder="""Example ASCII format:
project/
├── app.py
├── data/
│   ├── raw.json
│   └── clean.json
└── models/
    └── model.pkl"""
        )
    else:
        uploaded_file = st.file_uploader("Upload structure file", type=['txt', 'json', 'yaml', 'yml'])
        if uploaded_file:
            structure_text = uploaded_file.read().decode('utf-8')
            st.text_area("File contents:", value=structure_text, height=200, disabled=True)

with col2:
    st.subheader("⚙️ Settings")

    format_type = st.selectbox("Structure format:", ["ASCII", "JSON", "YAML"])

    # Use app workspace as base path
    default_base = os.path.join(os.getcwd(), "generated_structures")
    os.makedirs(default_base, exist_ok=True)

    base_path = st.text_input(
        "Base directory path:",
        value=default_base,
        help="Leave default to create inside app workspace"
    )

    dry_run = st.checkbox("🔍 Dry Run (Preview only)", value=False)
    st.info("💡 Uncheck 'Dry Run' to actually create files and folders")

    create_button = st.button("🚀 Create Project Structure", type="primary")

# -----------------------------
# Process the Structure
# -----------------------------
if create_button and structure_text:
    with st.spinner("Processing structure..."):
        parsed_structure = None
        if format_type == "ASCII":
            parsed_structure = parse_ascii(structure_text)
        elif format_type == "JSON":
            parsed_structure = parse_json(structure_text)
        elif format_type == "YAML":
            parsed_structure = parse_yaml(structure_text)

        if parsed_structure:
            issues = validate_structure(parsed_structure)
            if issues:
                st.error("❌ Structure validation failed:")
                for issue in issues:
                    st.error(f"• {issue}")
            else:
                if not os.path.exists(base_path):
                    st.error(f"❌ Base directory doesn't exist: {base_path}")
                else:
                    logs = create_structure(parsed_structure, base_path, dry_run)
                    st.success("✅ Structure processed successfully!")

                    st.subheader("📋 Results")
                    if dry_run:
                        st.info("🔍 DRY RUN MODE - No files were actually created")
                    else:
                        st.info("✅ Files and folders created successfully!")

                    for log in logs:
                        if "✅" in log:
                            st.success(log)
                        elif "📁" in log:
                            st.info(log)
                        elif "❌" in log:
                            st.error(log)
                        else:
                            st.write(log)

                    # Create ZIP for download if not dry run
                    if not dry_run:
                        zip_path = shutil.make_archive("project_structure", "zip", base_path)
                        with open(zip_path, "rb") as f:
                            st.download_button(
                                "📦 Download Project Structure (ZIP)",
                                f,
                                file_name="project_structure.zip",
                                mime="application/zip"
                            )

# -----------------------------
# Instructions
# -----------------------------
st.markdown("---")
st.subheader("📖 How to Use")

tab1, tab2, tab3 = st.tabs(["ASCII Format", "JSON Format", "YAML Format"])

with tab1:
    st.markdown("""
    **ASCII Tree Format:**
    ```
    project/
    ├── app.py
    ├── data/
    │   ├── raw.json
    │   └── clean.json
    └── models/
        └── model.pkl
    ```
    """)

with tab2:
    st.markdown("""
    **JSON Format:**
    ```json
    {
      "project": {
        "app.py": null,
        "data": {
          "raw.json": null,
          "clean.json": null
        },
        "models": {
          "model.pkl": null
        }
      }
    }
    ```
    """)

with tab3:
    st.markdown("""
    **YAML Format:**
    ```yaml
    project:
      app.py: null
      data:
        raw.json: null
        clean.json: null
      models:
        model.pkl: null
    ```
    """)

st.markdown("---")
st.caption("Built with ❤️ using Streamlit & Python")
