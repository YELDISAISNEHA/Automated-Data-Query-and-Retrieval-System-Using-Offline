import os
import pandas as pd
import pymongo
import ast
from pymongo import MongoClient
from langchain_community.chat_models import ChatOllama

# MongoDB Connection
def connect_mongodb():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["query_database"]
        collection = db["csv_data"]
        return collection
    except Exception as e:
        print("Error connecting to MongoDB:", e)
        return None

# Loads CSV file into MongoDB
def load_csv_to_mongo(csv_file, collection):
    try:
        df = pd.read_csv(csv_file)

        # Convert all object type columns to string
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str)
        # Clear existing data
        collection.delete_many({})  
        collection.insert_many(df.to_dict("records"))
        print("Data successfully loaded into MongoDB.")
    except Exception as e:
        print("Error loading CSV to MongoDB:", e)

# Generate MongoDB query by user input using LLM(TinyLLaMA via LangChain)
def generate_query(user_input, collection):
    # print(collection.find_one()) 
    sample_doc = collection.find_one()
    if not sample_doc:
        print("Collection is empty.")
        return None
    sample_doc.pop("_id", None)
    field_names = list(sample_doc.keys())
    print(field_names)
    llm = ChatOllama(model="tinyllama")

    prompt = f"""
You are a MongoDB expert. Only respond with a MongoDB query in this exact format:
db.collection.find({{ FILTER }})

Rules:
- Use only these fields: {field_names}
- All field names are case-sensitive.
- All values should match data types (e.g., string values in quotes).
- Do not use variables like $$ or $brand, only actual values from the request.

User request:
\"{user_input}\"
"""

    try:
        response = llm.invoke(prompt)
        query = response.content.strip()
        print("\nLLM Output:\n", query)

        # Extract query content from db.collection.find({...})
        if "db.collection.find(" in query:
            inner_start = query.find("find(") + len("find(")
            inner_end = query.find(")", inner_start)
            filter_text = query[inner_start:inner_end].strip()

            # Evaluate to Python dict safely
            query_dict = ast.literal_eval(filter_text)
            if isinstance(query_dict, dict):
                return query_dict
            else:
                print("Model returned non-dictionary.")
                return None
        else:
            print("Invalid format from LLM.")
            return None
    except Exception as e:
        print("Failed to parse LLM output:", e)
        return None

# Execute generated MongoDB Query on the given collection and return the all matching documents
def execute_query(query, collection):
    try:
        # print(list(collection.find(query)))
        return list(collection.find(query))
    except Exception as e:
        print("Error executing query:", e)
        return []

# Save or Display Results
def save_or_display(data, save=False, filename="output.csv"):
    if not data:
        print("No data to show or save.")
        return

    df = pd.DataFrame(data)
    df.drop(columns=["_id"], errors='ignore', inplace=True)

    if save:
        df.to_csv(filename, index=False)
        print(f"Saved to {filename}")
    else:
        print("\nQuery Result:\n")
        print(df.to_string(index=False))

# Main Driver
def main():
    collection = connect_mongodb()
    if collection is None:
        return

    csv_file = input("Enter data file path: ").strip()
    if not os.path.exists(csv_file):
        print("File not found.")
        return

    load_csv_to_mongo(csv_file, collection)

    while True:
        user_input = input("\nEnter your query (or 'exit'): ").strip()
        if user_input.lower() == "exit":
            break

        query = generate_query(user_input, collection)
        # if not query:
        #     print("Could not generate valid query.")
        #     continue

        data = execute_query(query, collection)
        if data:
            save_output = input("Save results to CSV? (yes/no): ").strip().lower()
            if save_output == "yes":
                filename = input("Enter filename (e.g., result.csv): ").strip()
                save_or_display(data, save=True, filename=filename)
            else:
                save_or_display(data, save=False)
        else:
            print("No matching documents found.")

if __name__ == "__main__":
    main()
