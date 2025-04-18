# Automated-Data-Query-and-Retrieval-System-Using-Offline

This project is an end-to-end intelligent data querying system that uses an LLM to generate and execute MongoDB queries from natural language user inputs. It enables CSV-to-MongoDB ingestion, AI-powered query generation, result retrieval, and optional saving of results.
**1. Project Structure**
```
├── main.py                   # The main Python script to run the system
├── sample_data.csv           # Sample CSV file (provided by you)
├── Queries_generated.txt     # Stores queries generated by the LLM for each test case
├── output.csv                # Sample output generated by the system
└── README.md                 # This file
```
**2. Requirements**
- Python
- MongoDB (running locally at localhost:27017)
- Required Python packages:
```bash
pip install pandas pymongo langchain langchain-community
```
**3. How to Use**
- **Start MongoDB**
  Ensure MongoDB is running locally on your machine.
  ```bash
  mongod
  ```
- **Install Ollama Locally**
  My system RAM is 4GB. Ollama models like mistral, gemma, llama2:7b (high parametered models) are not supported to my system which performs complex tasks than tinyllama. So I used tinyllama
  ```bash
  ollama pull tinyllama
  ```
- **Run the Script**
  ```bash
  python task.py
  ```
- Enter the path of CSV file you want to load.
- Type a user input query :
  What are the products with a price greater than $50?
- Type yes to save or display the output
