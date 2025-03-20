# Computer-Use-Agent--Windows

## Overview
**Computer-Use-Agent--Windows** is a project that enables AI-powered control of a Windows desktop environment using the latest Claude model from Anthropic. This project showcases how to integrate the **Anthropic API** to automate and interact with a Windows system efficiently.

## Getting Started
To use this project, you'll need an **Anthropic API key**. If you don't have one yet, you can sign up for free at [Anthropic Console](https://console.anthropic.com/).

### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- Docker (if using the containerized setup)([Docker desktop for windows](https://docs.docker.com/desktop/setup/install/windows-install/))
- Pip & Virtual Environment (recommended for local installation)

### Installation
#### 1️⃣ Clone the Repository
```sh
git clone https://github.com/Sir-Rotich6/Computer-Use-Agent--Windows.git
cd Computer-Use-Agent
```

#### 2️⃣ Set Up a Virtual Environment (Optional but Recommended)
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

#### 4️⃣ Set Up Environment Variables
Create a `.env` file in the project root and add:
```env
ANTHROPIC_API_KEY=your-api-key-here
```

#### 5️⃣ Run the Application
```sh
python main.py
```

## Docker Setup
For running the project in a containerized environment:
```sh
docker build -t computer-use-agent .
docker run --env-file .env computer-use-agent
```

## Features
- **AI-Powered Desktop Control**: Use Claude to execute Windows commands.
- **Secure Execution**: Only allows pre-approved operations for safety.
- **Customizable**: Extend functionality with additional commands.
- **Easy API Integration**: Uses the Anthropic API for seamless AI interactions.

## Resources
To learn more about working with Claude and the Anthropic API, check out:
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook)

## Contributing
We welcome contributions! Feel free to open an issue or submit a pull request.



## License
This project is licensed under the **http://www.apache.org/licenses/**. See the `LICENSE` file for details.
