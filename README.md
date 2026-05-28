# Project: Page Analyzer (Python Flask)

This is a website that analyzes specified pages for SEO suitability, similar to PageSpeed ​​Insights.

[View the running application](https://python-project-83-qwot.onrender.com)

## 📊 Project status 
| Tool | Status |
| :--- | :--- |
| **Hexlet tests**| [![Actions Status](https://github.com/Cheshire-12/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Cheshire-12/python-project-83/actions)|
| **Pytest and linter** | [![Python CI](https://github.com/Cheshire-12/python-project-83/actions/workflows/python-ci.yaml/badge.svg?branch=main)](https://github.com/Cheshire-12/python-project-83/actions/workflows/python-ci.yaml) |
| **Quality Gate Status** | [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Cheshire-12_python-project-83&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Cheshire-12_python-project-83) |
| **Code Smells** | [![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=Cheshire-12_python-project-83&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=Cheshire-12_python-project-83) |
| **Coverage** | [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=Cheshire-12_python-project-83&metric=coverage)](https://sonarcloud.io/summary/new_code?id=Cheshire-12_python-project-83) |

## 🛠️ Tech Stack
* **Backend:** Python, Flask, Gunicorn
* **Database:** PostgreSQL, Psycopg2 (Connection Pooling)
* **HTML Parsing:** BeautifulSoup4
* **Testing & CI:** Pytest, GitHub Actions, SonarQube Cloud
* **Frontend:** Bootstrap, Jinja2

### Prerequisites
* Python 3.12+
* PostgreSQL
* UV package manager

## 🛠 Installation
### 1. Clone the repository
Choose one method:
1. SSH (Requires SSH key setup):
```bash
git clone git@github.com:Cheshire-12/python-project-83.git
```
2. HTTPS (universal):
```bash
git clone https://github.com/Cheshire-12/python-project-83.git
```
### 2. Install dependencies

```bash
make install
```
### 3. Environment Configuration
Create a .env file in the root directory and add your credentials

Example:
```bash
DATABASE_URL=postgresql://username:password@localhost:5400/page_analyzer
SECRET_KEY=your_secret_key_here
```
### 4. Initialize Database
Create the required tables using the provided schema:
```bash
psql -d page_analyzer -f database.sql
```
### 5. Run the Application
```bash
make start 
# uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
```
## Testing
Run test:
```bash
make test
```
Lint code:
```bash
make lint
```
