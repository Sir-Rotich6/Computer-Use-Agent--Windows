---
## **Computer-Use-Agent--Windows**  
**Advanced Development Guide**  

### **🔧 Setup & Development**  

#### **1️⃣ Setup Environment**  
For Windows, use PowerShell:  
```powershell
python -m venv .venv  # Create virtual environment
.venv\Scripts\Activate  # Activate virtual environment
pip install -r requirements.txt  # Install dependencies
```

#### **2️⃣ Build Docker Image**  
```powershell
docker build . -t computer-use-agent:local
```

#### **3️⃣ Run the Container**  
Replace `$env:ANTHROPIC_API_KEY` with your actual API key:  
```powershell
docker run -e ANTHROPIC_API_KEY=$env:ANTHROPIC_API_KEY `
    -v ${PWD}/computer_use_agent_demo:/home/computeruse/computer_use_agent_demo/ `
    -v $HOME/.anthropic:/home/computeruse/.anthropic `
    -p 5900:5900 -p 8501:8501 -p 6080:6080 -p 8080:8080 `
    -it computer-use-agent:local
```

### **🛠️ Testing & Code Quality**  

#### **Lint Code (Check for Issues)**  
```powershell
ruff check .
```

#### **Format Code**  
```powershell
ruff format .
```

#### **Type Checking**  
```powershell
pyright
```

#### **Run Tests**  
Run all tests:  
```powershell
pytest
```
Run a specific test:  
```powershell
pytest tests\path_to_test.py::test_name -v
```

### **📏 Code Style Guide**  

#### **Python Standards**  
- **Naming Conventions**:  
  - Functions & variables → `snake_case`  
  - Classes → `PascalCase`  
- **Imports**:  
  - Use `isort` to organize  
  - Combine `as` imports  
- **Error Handling**:  
  - Define custom `ToolError` for specific tool-related errors  
- **Type Annotations**:  
  - Add type hints for **all** parameters & return types  
- **Class Structure**:  
  - Prefer `dataclasses`  
  - Use abstract base classes where applicable  

---
