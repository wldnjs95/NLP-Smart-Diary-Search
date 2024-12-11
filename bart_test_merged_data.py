# -*- coding: utf-8 -*-
"""bart_test_merged_data.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1UtwuOtd6xCdGQQ5bqWNPzbWUaURqwgQd
"""

!pip install transformers datasets torch
!pip install datasets
!pip install transformers datasets pandas scikit-learn
!pip install --upgrade gradio
!pip install sentence-transformers

import json
import torch
from transformers import BartTokenizer, BartForConditionalGeneration, AdamW

# Load JSON data
json_file_path = "combined_diary.json"
with open(json_file_path, "r") as file:
    diary_data_direct = json.load(file)

# Prepare data for Seq2Seq with BART
def prepare_data(data):
    input_texts = []
    target_texts = []

    for diary_id, diary_content in data.items():
        diary_entry = diary_content["diary_entry"]
        keywords = diary_content["extracted_keywords"]

        # Input prompt
        input_text = f"Extract Event, Action, Time, and Thoughts from: '{diary_entry}'"

        # Target output
        target_text = json.dumps(keywords)

        input_texts.append(input_text)
        target_texts.append(target_text)

    return input_texts, target_texts

# Prepare inputs and outputs
input_texts, target_texts = prepare_data(diary_data_direct)

# Load tokenizer and model
model_name = "facebook/bart-base"
tokenizer = BartTokenizer.from_pretrained(model_name)
model = BartForConditionalGeneration.from_pretrained(model_name)

# Tokenization for Seq2Seq
def tokenize_data(input_texts, target_texts, tokenizer):
    inputs = tokenizer(input_texts, max_length=512, truncation=True, padding="max_length", return_tensors="pt")
    targets = tokenizer(target_texts, max_length=512, truncation=True, padding="max_length", return_tensors="pt")
    return inputs, targets

inputs, targets = tokenize_data(input_texts, target_texts, tokenizer)

# Optimizer
optimizer = AdamW(model.parameters(), lr=1e-5)

# Fine-tuning loop
num_epochs = 3
model.train()

for epoch in range(num_epochs):
    total_loss = 0

    for i in range(len(inputs["input_ids"])):
        input_ids = inputs["input_ids"][i].unsqueeze(0)  # Add batch dimension
        attention_mask = inputs["attention_mask"][i].unsqueeze(0)
        labels = targets["input_ids"][i].unsqueeze(0)  # Add batch dimension

        # Forward pass
        optimizer.zero_grad()
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        total_loss += loss.item()

        # Backward pass
        loss.backward()
        optimizer.step()

    avg_loss = total_loss / len(inputs["input_ids"])
    print(f"Epoch {epoch + 1} Average Loss: {avg_loss}")

    # Save model after each epoch
    #model_save_path = f"bart_finetuned_epoch_{epoch + 1}.pt"
    #torch.save(model.state_dict(), model_save_path)
    #print(f"Model saved after epoch {epoch + 1} to {model_save_path}")

#save the model
save_directory = "fine_tuned_bart1"
model.save_pretrained(save_directory)
tokenizer.save_pretrained(save_directory)
print(f"Model saved to {save_directory}")


# Testing the model
model.eval()

def test_model(diary_entry):
    input_text = f"Extract Event, Action, Time, and Thoughts from: '{diary_entry}'"
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512)

    with torch.no_grad():
        generated_ids = model.generate(
            inputs["input_ids"],
            max_length=100,
            num_beams=4,
            early_stopping=True
        )
        output = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
    return output

# Test Entries
test_entries = [
    "I woke up to the gentle sound of dripping water. The air was heavy with humidity, clinging to my skin. The house felt unusually quiet, as if holding its breath. Stepping outside, I noticed puddles forming under a gray sky. A light rain had begun, soft and soothing, bringing a sense of calm. It felt like the world was pausing, just for a moment.",
    "The party started at 4 PM, and by midnight, it still showed no signs of ending. Laughter and music filled the air as plates piled up and drinks kept flowing. I watched as conversations turned deeper, and some danced like no one was watching. Though I felt tired, I couldn’t help but smile—it’s rare to experience such a lively night. The clock ticked past midnight, but no one seemed to care.",
    "The flight to London, once $600, skyrocketed to $3600 in just four days. I stared at the screen in disbelief, refreshing the page as if hoping it was a glitch. Planning the trip felt exciting at first, but now it seemed almost impossible. I wondered if I should wait, gamble on a price drop, or let the dream go for now. Travel, it seems, has its own way of testing patience."
]

# Generate predictions for test entries
for idx, entry in enumerate(test_entries):
    print(f"Test Entry {idx + 1}: {entry}")
    prediction = test_model(entry)
    print(f"Predicted Output {idx + 1}: {prediction}\n")

from huggingface_hub import HfApi, upload_folder

# Define your token
HF_TOKEN = "insert_token"

# Create a repo
api = HfApi()
api.create_repo(repo_id="mk43275/bart_base_model_1", token=HF_TOKEN)

# Upload your model
upload_folder(
    folder_path="fine_tuned_bart1",  # Path to the model folder
    path_in_repo="",
    repo_id="mk43275/bart_base_model_1",
    token=HF_TOKEN
)

import os
import shutil
from transformers import PreTrainedTokenizer, PreTrainedModel

# Function to save the fine-tuned model and tokenizer
def save_model_and_tokenizer(model, tokenizer, save_directory):
    """
    Saves the fine-tuned model and tokenizer to the specified directory.

    Args:
        model (PreTrainedModel): The fine-tuned BART model.
        tokenizer (PreTrainedTokenizer): The tokenizer used with the model.
        save_directory (str): Directory path to save the model and tokenizer.
    """
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    model.save_pretrained(save_directory)
    tokenizer.save_pretrained(save_directory)
    print(f"Model and tokenizer saved to {save_directory}")

    # Compress the directory into a zip file
    zip_filename = save_directory + ".zip"
    shutil.make_archive(save_directory, 'zip', save_directory)
    print(f"Model and tokenizer zipped into {zip_filename}")

# Directory to save the model and tokenizer
save_directory = "fine_tuned_bart_model"

# Save model and tokenizer after training
save_model_and_tokenizer(model, tokenizer, save_directory)

# Load the model and tokenizer to verify
from transformers import BartTokenizer, BartForConditionalGeneration

# Load the model and tokenizer from the saved directory
tokenizer = BartTokenizer.from_pretrained(save_directory)
model = BartForConditionalGeneration.from_pretrained(save_directory)

print("Model and tokenizer successfully loaded!")

import os
import json
import pandas as pd
import gradio as gr
from transformers import BartTokenizer, BartForConditionalGeneration

#load the fine-tuned model and tokenizer
model_path = "fine_tuned_bart1"  #path to the fine-tuned BART model
tokenizer = BartTokenizer.from_pretrained(model_path)
model = BartForConditionalGeneration.from_pretrained(model_path)

#extract details using the fine-tuned model
def extract_details(entry):
    inputs = tokenizer(entry, return_tensors="pt", truncation=True, max_length=512)
    outputs = model.generate(
        inputs["input_ids"], max_length=128, num_beams=4, early_stopping=True
    )
    decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return decoded_output

#save a diary entry to a JSON file (option 1)
def save_entry(file_name, entry):
    if not file_name.endswith(".json"):
        file_name += ".json"

    #load the JSON file
    if not os.path.exists(file_name):
        data = []
    else:
        with open(file_name, "r") as f:
            data = json.load(f)

    #extract details from the entry
    details = extract_details(entry)

    #add entry to the dataset
    entry_num = len(data) + 1
    data.append({"diary_entry_num": entry_num, "diary_entry": entry, "extracted_details": details})

    #save the updated dataset
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)

    return f"Entry saved successfully to {os.path.abspath(file_name)}"

#upload a CSV file (option 2)
def upload_csv(file_obj, file_name):
    if not file_name.endswith(".csv"):
        file_name += ".csv"

    #save the uploaded file locally
    file_path = file_obj.name
    uploaded_df = pd.read_csv(file_path)

    #validate the file structure
    if "diary_entry_num" not in uploaded_df.columns or "diary_entry" not in uploaded_df.columns:
        return "Invalid file format. The file must contain 'diary_entry_num' and 'diary_entry' columns."

    #save locally as the given name
    uploaded_df.to_csv(file_name, index=False)
    return f"File uploaded successfully and saved as {file_name}."

#search diary entries in a given CSV file (search system)
def search_csv(file_name, keyword):
    if not file_name.endswith(".csv"):
        file_name += ".csv"

    if not os.path.exists(file_name):
        return "File not found. Please check the file name or upload a file first."

    #load the data
    df = pd.read_csv(file_name)

    #filter entries by keyword
    results = df[df["diary_entry"].str.contains(keyword, case=False, na=False)]

    if results.empty:
        return "No matching entries found."

    #format results
    formatted_results = []
    for _, row in results.iterrows():
        formatted_results.append(
            f"Entry #{int(row['diary_entry_num'])}:\nDiary Entry: {row['diary_entry']}\n"
        )
    return "\n".join(formatted_results)

#gradio UI demo
with gr.Blocks() as diary_ui:
    gr.Markdown("# 📖 Enhanced Diary Entry System")
    gr.Markdown("### Save your diary entries manually, upload a CSV file, or search existing entries.")

    with gr.Tab("Write Diary"):
        gr.Markdown("### Write a new diary entry and save it.")
        file_name = gr.Textbox(label="File Name", placeholder="Enter a name for your JSON file (e.g., my_diary)")
        diary_entry = gr.Textbox(label="Diary Entry", lines=5, placeholder="Write your diary entry here...")
        save_button = gr.Button("Save Entry")
        save_message = gr.Textbox(label="Save Message", interactive=False)
        save_button.click(save_entry, inputs=[file_name, diary_entry], outputs=save_message)

    with gr.Tab("Upload CSV"):
        gr.Markdown("### Upload a CSV file for diary entries.")
        csv_file_input = gr.File(label="Upload CSV File")
        uploaded_csv_name = gr.Textbox(label="Save As", placeholder="Enter a name for the uploaded CSV file (e.g., uploaded_diary)")
        upload_button = gr.Button("Upload")
        upload_message = gr.Textbox(label="Upload Status", interactive=False)
        upload_button.click(upload_csv, inputs=[csv_file_input, uploaded_csv_name], outputs=upload_message)

    with gr.Tab("Search Diary"):
        gr.Markdown("### Search diary entries by keyword in an uploaded CSV file.")
        file_name_search = gr.Textbox(label="CSV File Name", placeholder="Enter the name of your CSV file")
        search_keyword = gr.Textbox(label="Search Keyword", placeholder="Enter a keyword to search for...")
        search_button = gr.Button("Search")
        search_results = gr.Textbox(label="Search Results", interactive=False, lines=10)
        search_button.click(search_csv, inputs=[file_name_search, search_keyword], outputs=search_results)

#launch the Gradio app
diary_ui.launch()

"""### ner w test"""

import pandas as pd
import torch
from transformers import BartForConditionalGeneration, BartTokenizer

#load the fine-tuned model and tokenizer
model_name = "fine_tuned_bart1"
model = BartForConditionalGeneration.from_pretrained(model_name)
tokenizer = BartTokenizer.from_pretrained(model_name)

#load the test dataset
file_path = "test-diary-30-fm.csv"
test_data = pd.read_csv(file_path)

#extract diary entries
texts = test_data['diary_entry'].tolist()

#task-specific prompt
def test_model(diary_entry):
    input_text = f"Extract Event, Action, Time, and Thoughts from: '{diary_entry}'"
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512)

    with torch.no_grad():
        generated_ids = model.generate(
            inputs["input_ids"],
            max_length=100,
            num_beams=4,
            early_stopping=True
        )
        output = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
    return output

#gnerate predictions for CSV data
structured_results = []
for text in texts:
    prediction = test_model(text)
    try:
        structured_output = json.loads(prediction)  #parse JSON if possible
    except json.JSONDecodeError:
        structured_output = {"event": None, "action": None, "time": None, "thought": None}
    structured_results.append({"text": text, "predicted": structured_output})

#display results
for result in structured_results:
    print(f"Input Text: {result['text']}")
    print("NER Prediction:")
    for key, value in result["predicted"].items():
        print(f"  {key}: {value}")
    print("-" * 50)

# Prepare data for saving
output_data = []
for result in structured_results:
    entry = {"diary_entry": result["text"]}
    entry.update(result["predicted"])  # Add the predicted fields to the dictionary
    output_data.append(entry)

# Convert to DataFrame
output_df = pd.DataFrame(output_data)

# Save the DataFrame to a CSV file
output_file_path = "diary_predictions.csv"
output_df.to_csv(output_file_path, index=False)

print(f"Predictions saved to {output_file_path}")
