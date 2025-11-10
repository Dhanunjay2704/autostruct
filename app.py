import streamlit as st
import os
import json
import yaml
import re
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

# ASCII parser
# ASCII parser
def parse_ascii(text):
    """Parse ASCII tree format into dictionary structure"""
    lines = text.strip().split('\n')
    result = {}
    stack = [(result, -1)]  # (current_dict, indent_level)
    
    for line in lines:
        if not line.strip():
            continue
            
        # Calculate indentation - count position of actual content
        original_line = line
        indent = 0
        content_start = 0
        
        # Find where actual content starts (after tree characters)
        for i, char in enumerate(line):
            if char in ' \t│':
                if char == '\t':
                    indent += 4
                else:
                    indent += 1
            elif char in '├└┌┐┘┬┴┼─':
                # Tree drawing character, but content might be after it
                content_start = i + 1
                # Look for spaces after tree character
                while content_start < len(line) and line[content_start] in ' ─':
                    content_start += 1
                    indent += 1
                break
            else:
                content_start = i
                break
        
        # Extract the actual file/folder name
        if content_start < len(line):
            cleaned = line[content_start:].strip()
        else:
            cleaned = line.strip()
            
        
        # Additional cleaning for complex tree characters
        cleaned = re.sub(r'^[├└│─┌┐┘┬┴┼\s]*', '', cleaned)
        cleaned = re.sub(r'[├└│─┌┐┘┬┴┼]+\s*', '', cleaned).strip()
        
        # Handle cases where there might be extra spaces or dashes
        cleaned = re.sub(r'^[\s─]+', '', cleaned)
        cleaned = re.sub(r'[\s─]+$', '', cleaned)
        
        if not cleaned:
            continue
            
        # Pop from stack until we find the correct parent level
        while len(stack) > 1 and stack[-1][1] >= indent:
            stack.pop()
            
        current_dict = stack[-1][0]
        
        # Determine if it's a folder or file
        if cleaned.endswith('/'):
            # It's a folder
            folder_name = cleaned[:-1]
            if folder_name:
                current_dict[folder_name] = {}
                stack.append((current_dict[folder_name], indent))
        else:
            # It's a file
            if cleaned:
                current_dict[cleaned] = None
                
    return result

# JSON parser
def parse_json(text):
    """Parse JSON format into dictionary structure"""
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON format: {e}")
        return None

# YAML parser
def parse_yaml(text):
    """Parse YAML format into dictionary structure"""
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as e:
        st.error(f"Invalid YAML format: {e}")
        return None

# Structure validator
def validate_structure(structure, path=""):
    """Validate the structure for issues"""
    issues = []
    
    def validate_recursive(obj, current_path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                # Check for invalid characters in names
                if re.search(r'[<>:"|?*]', key):
                    issues.append(f"Invalid characters in name: {current_path}/{key}")
                
                new_path = f"{current_path}/{key}" if current_path else key
                if value is None:
                    # It's a file
                    pass
                elif isinstance(value, dict):
                    # It's a folder
                    validate_recursive(value, new_path)
                    
    validate_recursive(structure)
    return issues

# Structure creator
def create_structure(structure, base_path, dry_run=False):
    """Create the actual folder/file structure"""
    logs = []
    
    def create_recursive(obj, current_path):
        if not isinstance(obj, dict):
            return
            
        for key, value in obj.items():
            full_path = os.path.join(current_path, key)
            
            try:
                if value is None or value == "":
                    # It's a file
                    if not dry_run:
                        # Ensure parent directory exists
                        parent_dir = os.path.dirname(full_path)
                        if parent_dir and not os.path.exists(parent_dir):
                            os.makedirs(parent_dir, exist_ok=True)
                        
                        # Create the file
                        with open(full_path, 'w') as f:
                            pass  # Create empty file
                    logs.append(f"✅ {'[DRY RUN] ' if dry_run else ''}Created file: {full_path}")
                    
                elif isinstance(value, dict):
                    # It's a folder
                    if not dry_run:
                        os.makedirs(full_path, exist_ok=True)
                    logs.append(f"📁 {'[DRY RUN] ' if dry_run else ''}Created folder: {full_path}")
                    
                    # Recursively create contents
                    create_recursive(value, full_path)
                    
                elif isinstance(value, list):
                    # Handle YAML list format
                    if not dry_run:
                        os.makedirs(full_path, exist_ok=True)
                    logs.append(f"📁 {'[DRY RUN] ' if dry_run else ''}Created folder: {full_path}")
                    
                    # Process list items
                    for item in value:
                        if isinstance(item, str):
                            # Simple file
                            file_path = os.path.join(full_path, item)
                            if not dry_run:
                                with open(file_path, 'w') as f:
                                    pass
                            logs.append(f"✅ {'[DRY RUN] ' if dry_run else ''}Created file: {file_path}")
                        elif isinstance(item, dict):
                            # Nested structure
                            create_recursive(item, full_path)
                    
            except Exception as e:
                logs.append(f"❌ Error creating {full_path}: {str(e)}")
    
    if isinstance(structure, dict):
        create_recursive(structure, base_path)
    
    return logs

# Main UI
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Input Structure")
    
    # Input method selection
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
     
    else:  # Upload File
        uploaded_file = st.file_uploader(
            "Upload structure file",
            type=['txt', 'json', 'yaml', 'yml']
        )
        if uploaded_file:
            structure_text = uploaded_file.read().decode('utf-8')
            st.text_area("File contents:", value=structure_text, height=200, disabled=True)

with col2:
    st.subheader("⚙️ Settings")
    
    # Format selection
    format_type = st.selectbox(
        "Structure format:",
        ["ASCII", "JSON", "YAML"]
    )
    
    # Base path input
    base_path = st.text_input(
        "Base directory path:",
        value=os.path.expanduser("~"),
        help="Enter the full path where you want to create the structure"
    )
    
    # Dry run option
    dry_run = st.checkbox("🔍 Dry Run (Preview only)", value=False)
    st.info("💡 Uncheck 'Dry Run' to actually create files and folders")
    
    # Create button
    create_button = st.button("🚀 Create Project Structure", type="primary")

# Process the structure
if create_button and structure_text:
    with st.spinner("Processing structure..."):
        # Parse based on selected format
        parsed_structure = None
        
        if format_type == "ASCII":
            parsed_structure = parse_ascii(structure_text)
        elif format_type == "JSON":
            parsed_structure = parse_json(structure_text)
        elif format_type == "YAML":
            parsed_structure = parse_yaml(structure_text)
        
        if parsed_structure:
            # Validate structure
            issues = validate_structure(parsed_structure)
            
            if issues:
                st.error("❌ Structure validation failed:")
                for issue in issues:
                    st.error(f"  • {issue}")
            else:
                # Validate base path
                if not os.path.exists(base_path):
                    st.error(f"❌ Base directory doesn't exist: {base_path}")
                elif not os.path.isdir(base_path):
                    st.error(f"❌ Base path is not a directory: {base_path}")
                else:
                    # Create structure
                    logs = create_structure(parsed_structure, base_path, dry_run)
                    
                    # Display results
                    st.success("✅ Structure processed successfully!")
                    
                    # Show logs
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
                    
                    # Show parsed structure for debugging
                    with st.expander("🔍 Parsed Structure (for debugging)"):
                        st.json(parsed_structure)

# Instructions section
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
    - Folders end with `/`
    - Use tree characters or simple indentation
    - Files don't need special notation
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
    - Folders are objects `{}`
    - Files are `null` values
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
    - Folders contain nested items
    - Files have `null` values
    """)

# Footer
st.markdown("---")
