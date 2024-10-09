#Calculate EW, MW 
#
#EW is gone
#
# 1. Figure replication 
#     1. Top 10 words  
#     2. k_lemma in analysis: 10, -50
#     3. 50, 10, 1  + negative versions
#     4. Just EW
# 2. Data table replication
#     1. GPT2 BERT-CASED
#     2. Evaluate/ROI (MW)
#         1. Then calculate the score via a custom script
#     3. Minpair analyze (EW)
#     4. 
import json
import os
import csv
import time
import pandas as pd


#We have to use all of the verbs
def process_csv(fileName) -> list:
    with open(fileName, "r", encoding="utf-8") as csvFile:
        verbList = []
        i = 0 
        for line in csvFile:
            if i > 0:
                line = line[2:-3].strip()
                verbs = line.split(",")
                verbList.append((verbs[0], verbs[1]))
            i += 1
    return verbList



def process_data():
    # {"sentence_good": "the consultant smiles", "sentence_bad": "the consultant smile", "label": -1}

    def simple_verb_process(fileName, lineList: list, numContext, condition, verbList, sentSet, tsv_file):
        writer = csv.writer(tsv_file, delimiter='\t')

        # Define a limited set of verbs to use
        allowed_verbs = {'is', 'are', 'bring', 'gives', 'help'}  # Add or modify the verbs as needed
        bring = {'bring', 'brings'}
        
        # Track the number of processed sentences
        processed_sentences = 0
        max_sentences_per_file = 100

        with open(fileName, 'r', encoding="utf-8") as jsonlFile:
            for line in jsonlFile:
                if processed_sentences >= max_sentences_per_file:
                    break  # Stop processing if the limit is reached
                
                line = line.strip()
                if line:
                    data = json.loads(line)
                    good_sent = data['sentence_good']
                    bad_sent = data['sentence_bad'] 
                    
                    # Step: Try to make a template sentence and then run the rest of the verbs through it 
                    pairID = (len(lineList)//2) + 1
                    sent_arr = good_sent.split()
                    
                    # Determine the verb index and ROI based on the sentence structure
                    if len(sent_arr) >= 4 and sent_arr[-4] in bring:
                        verbInd = -4
                        roi = len(sent_arr) - 4
                    elif len(sent_arr) >= 2 and sent_arr[-2] in allowed_verbs:
                        verbInd = -2
                        roi = len(sent_arr) - 2
                    else:
                        verbInd = -1
                        roi = len(sent_arr) - 1
                    
                    sent_arr[verbInd] = '_'
                    template_sentence = " ".join(sent_arr)
                    
                    if template_sentence not in sentSet:
                        sentSet.add(template_sentence)     
                        
                        # Ensure that only allowed verbs are used in output
                        for verb in allowed_verbs:
                            # Add good sentence
                            good_sent = template_sentence.replace('_', verb)
                            writer.writerow([len(lineList)+1, "expected", pairID, numContext, verb, condition, "NA", good_sent, roi])
                            
                            # Add bad sentence
                            bad_sent = template_sentence.replace('_', verb)
                            writer.writerow([len(lineList)+1, "unexpected", pairID, numContext, verb, condition, "NA", bad_sent, roi])
                            pairID += 1

                    processed_sentences += 1  # Increment the count of processed sentences
        return sentSet


    csv_file = "combined_verb_list.csv"
    verbList = process_csv(csv_file)
    lineList = []
    numContext = 1
    sentSet = set()

    # ['sentID', 'comparison', 'pairid', 'contextid', 'lemma', 'condition', 'pronoun', 'sentence', 'ROI']    
    with open('midterm_output.tsv', 'a', newline='') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        writer.writerow(['sentID', 'comparison', 'pairid', 'contextid', 'lemma', 'condition', 'pronoun', 'sentence', 'ROI'])
        for folder_name in os.listdir('data_categories'):
            in_folder_path = os.path.join('data_categories', folder_name)
            print(folder_name)
            for file in os.listdir(in_folder_path):
                file_path = os.path.join(in_folder_path, file)
                if os.path.isfile(file_path):
                    condition = folder_name
                    simple_verb_process(file_path, lineList, numContext, condition, verbList, sentSet, tsv_file)

            numContext += 1
   



#have to deal with is/are 


#1. Rename the templates
#2. Make the conditions
#3. Run the data, add the blimp  



def data_table_replication():
    


    pass


def main():
    t1 = time.time()

    process_data()

    t2 = time.time()

    print('Time to run', t2-t1)


if __name__ == "__main__":
    main()