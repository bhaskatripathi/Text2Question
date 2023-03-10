import gradio as gr
import requests
import os
import numpy as np
import pandas as pd
import json
import socket
import huggingface_hub
from huggingface_hub import Repository
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForSequenceClassification
from questiongenerator import QuestionGenerator
import csv
from urllib.request import urlopen
import re as r

qg = QuestionGenerator()

HF_TOKEN = os.environ.get("HF_TOKEN")
DATASET_NAME = "question_generation_T5_dataset"
DATASET_REPO_URL = f"https://huggingface.co/datasets/pragnakalp/{DATASET_NAME}"
DATA_FILENAME = "que_gen_logs.csv"
DATA_FILE = os.path.join("que_gen_logs", DATA_FILENAME)
DATASET_REPO_ID = "pragnakalp/question_generation_T5_dataset"
print("is none?", HF_TOKEN is None)
article_value = """Google was founded in 1998 by Larry Page and Sergey Brin while they were Ph.D. students at Stanford University in California. Together they own about 14 percent of its shares and control 56 percent of the stockholder voting power through supervoting stock. They incorporated Google as a privately held company on September 4, 1998. An initial public offering (IPO) took place on August 19, 2004, and Google moved to its headquarters in Mountain View, California, nicknamed the Googleplex. In August 2015, Google announced plans to reorganize its various interests as a conglomerate called Alphabet Inc. Google is Alphabet's leading subsidiary and will continue to be the umbrella company for Alphabet's Internet interests. Sundar Pichai was appointed CEO of Google, replacing Larry Page who became the CEO of Alphabet."""
# REPOSITORY_DIR = "data"
# LOCAL_DIR = 'data_local'
# os.makedirs(LOCAL_DIR,exist_ok=True)

try:
    hf_hub_download(
        repo_id=DATASET_REPO_ID,
        filename=DATA_FILENAME,
        cache_dir=DATA_DIRNAME,
        force_filename=DATA_FILENAME
    )
    
except:
    print("file not found")

repo = Repository(
    local_dir="que_gen_logs", clone_from=DATASET_REPO_URL, use_auth_token=HF_TOKEN
)


def getIP():
    ip_address = ''
    try:
    	d = str(urlopen('http://checkip.dyndns.com/')
    			.read())
    
    	return r.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(d).group(1)
    except Exception as e:
        print("Error while getting IP address -->",e)
        return ip_address

def get_location(ip_addr):
    location = {}
    try:
        ip=ip_addr
    
        req_data={
            "ip":ip,
            "token":"pkml123"
        }
        url = "https://demos.pragnakalp.com/get-ip-location"
    
        # req_data=json.dumps(req_data)
        # print("req_data",req_data)
        headers = {'Content-Type': 'application/json'}
    
        response = requests.request("POST", url, headers=headers, data=json.dumps(req_data))
        response = response.json()
        print("response======>>",response)
        return response
    except Exception as e:
        print("Error while getting location -->",e)
        return location
    
def generate_questions(article,num_que):
    result = ''
    if article.strip():
        if num_que == None or num_que == '':
            num_que = 3
        else:
            num_que = num_que
        generated_questions_list = qg.generate(article, num_questions=int(num_que))
        summarized_data = {
            "generated_questions" : generated_questions_list
        }
        generated_questions = summarized_data.get("generated_questions",'')
            
        for q in generated_questions:
            print(q)
            result = result + q + '\n'
        save_data_and_sendmail(article,generated_questions,num_que)
        print("sending result***!!!!!!", result)
        return result
    else:
        raise gr.Error("Please enter text in inputbox!!!!")
   
"""
Save generated details
"""
def save_data_and_sendmail(article,generated_questions,num_que):
    try:
        ip_address= getIP()
        print(ip_address)
        location = get_location(ip_address)
        print(location)
        add_csv = [article, generated_questions, num_que, ip_address,location]
        print("data^^^^^",add_csv)
        with open(DATA_FILE, "a") as f:
            writer = csv.writer(f)
            # write the data
            writer.writerow(add_csv)
            commit_url = repo.push_to_hub()
            print("commit data   :",commit_url)
            
        url = 'https://pragnakalpdev35.pythonanywhere.com/HF_space_que_gen'
        # url = 'http://pragnakalpdev33.pythonanywhere.com/HF_space_question_generator'
        myobj = {'article': article,'total_que': num_que,'gen_que':generated_questions,'ip_addr':ip_address,'loc':location}
        x = requests.post(url, json = myobj) 
        print("myobj^^^^^",myobj)

    except Exception as e:
        return "Error while sending mail" + str(e)
        
    return "Successfully save data"

## design 1
inputs=gr.Textbox(value=article_value, lines=5, label="Input Text/Article",elem_id="inp_div")
total_que = gr.Textbox(label="Number of questions to generate",elem_id="inp_div")
outputs=gr.Textbox(label="Generated Questions",lines=6,elem_id="inp_div")

demo = gr.Interface(
    generate_questions,
    [inputs,total_que],
    outputs,
    title="Question Generation Using T5-Base Model",
    css=".gradio-container {background-color: lightgray} #inp_div {background-color: #7FB3D5;}",
    article="""<p style='text-align: center;'>Feel free to give us your <a href="https://www.pragnakalp.com/contact/" target="_blank">feedback</a> on this Question Generation using T5 demo.</p>
                                        <p style='text-align: center;'>Developed by: <a href="https://www.pragnakalp.com" target="_blank">Pragnakalp Techlabs</a></p>"""
    
)
demo.launch()
