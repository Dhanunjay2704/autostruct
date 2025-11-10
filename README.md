
# 🏗️ AutoStruct – Project Structure Generator

AutoStruct is a **Streamlit-based tool** that helps you generate clean, ready-to-use **project folder and file structures** instantly from **ASCII trees, JSON, or YAML** input formats.

This is especially useful for developers, students, and data scientists who want to quickly set up standardized project structures without manually creating folders and files.

---

## 🚀 Features

* 📂 **Multi-format Input**

  * ASCII Tree format
  * JSON format
  * YAML format

* 🔍 **Validation**

  * Detects invalid characters in names
  * Ensures proper folder/file structure

* ⚙️ **Modes**

  * **Dry Run Mode** → Preview the structure before creating it
  * **Create Mode** → Actually generates the files & folders

* ✅ **Cross-Platform Support**
  Works on **Windows, macOS, and Linux**

---

## 📸 Demo Screenshot
<img width="1897" height="925" alt="image" src="https://github.com/user-attachments/assets/7f5f314e-adf5-413d-b64b-c8c55b9e4a37" />


## 📝 Example Inputs

### 1. ASCII Format

```
project/
├── app.py
├── data/
│   ├── raw.json
│   └── clean.json
└── models/
    └── model.pkl
```

### 2. JSON Format

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

### 3. YAML Format

```yaml
project:
  app.py: null
  data:
    raw.json: null
    clean.json: null
  models:
    model.pkl: null
```

---

## 🛠️ Installation & Setup

1. **Clone the repo**

   ```bash
   git clone https://github.com/your-username/autostruct.git
   cd autostruct
   ```

2. **Create a virtual environment (optional but recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**

   ```bash
   streamlit run app.py
   ```

---

## ⚡ Usage

1. Choose **input method**: Paste text or upload a file (`.txt`, `.json`, `.yaml`, `.yml`).
2. Select **structure format**: ASCII / JSON / YAML.
3. Enter the **base directory path** where you want the structure.
4. Enable/disable **Dry Run mode**.
5. Click **“🚀 Create Project Structure”**.

---

## 📂 Project Structure (of this tool)

```
autostruct/
├── app.py          # Main Streamlit app
├── requirements.txt
├── README.md
```

---

## ✅ Requirements

* Python 3.8+
* Streamlit
* PyYAML

(install via `pip install -r requirements.txt`)

---

