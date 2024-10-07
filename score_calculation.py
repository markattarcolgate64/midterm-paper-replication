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
    #{"sentence_good": "the consultant smiles", "sentence_bad": "the consultant smile", "label": -1}

    
    def simple_verb_process(fileName, lineList: list, numContext, condition, verbList, sentSet, tsv_file):

        writer = csv.writer(tsv_file, delimiter='\t')

        basic_verbs = {'is', 'are', 'interest'}
        bring = {'bring', 'brings'}
        
        with open(fileName, 'r', encoding="utf-8") as jsonlFile:
            for line in jsonlFile:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    # sentid	comparison	pairid	contextid	lemma	condition	pronoun	sentence	ROI
                    #we need to get good/bad sentence
                    good_sent = data['sentence_good']
                    bad_sent = data['sentence_bad'] 
                    
                    #step: try to make a template sentence and then run the rest of the verbs through it 
                    pairID = (len(lineList)//2) + 1
                    sent_arr = good_sent.split()
                    if len(sent_arr) >= 4 and sent_arr[-4] in bring:
                        verbInd = -4
                        roi = len(sent_arr) - 4
                    if len(sent_arr) >= 2 and sent_arr[-2] in basic_verbs:
                        verbInd = -2
                        roi = len(sent_arr) - 2
                    else:
                        verbInd = -1
                        roi = len(sent_arr) -1
                    
                    sent_arr[verbInd] = '_'
                    template_sentence = " ".join(sent_arr)
                    with open('output.tsv', 'a', newline='') as tsv_file:
                        if template_sentence not in sentSet:
                            sentSet.add(template_sentence)     
                            #deal with adding is/are 
                            if verbInd != -2:
                                temp_sent_arr = template_sentence.split()

                                for gV, bV in verbList:
                                    #add good sentence
                                    temp_sent_arr[verbInd] = gV
                                    good_sent = " ".join(temp_sent_arr)
                                    writer.writerow([len(lineList)+1, "expected", pairID, numContext, gV, condition, "NA", good_sent, roi])
                                    #lineList.append([len(lineList)+1, "expected", pairID, numContext, gV, condition, "NA", good_sent, roi])

                                    temp_sent_arr[verbInd] = bV
                                    bad_sent = " ".join(temp_sent_arr)
                                    #add bad sentence
                                    #lineList.append([len(lineList)+1, "unexpected", pairID, numContext, bV, condition, "NA", bad_sent, roi])
                                    writer.writerow([len(lineList)+1, "expected", pairID, numContext, bV, condition, "NA", bad_sent, roi])

                                    pairID += 1
                            else:
                                #lineList.append([len(lineList)+1, "expected", pairID, numContext, "BE", condition, "NA", good_sent, roi])
                                writer.writerow([len(lineList)+1, "expected", pairID, numContext, "BE", condition, "NA", good_sent, roi])
                                    #add bad sentence
                                #lineList.append([len(lineList)+1, "unexpected", pairID, numContext, "BE", condition, "NA", bad_sent, roi])
                                writer.writerow([len(lineList)+1, "unexpected", pairID, numContext, "BE", condition, "NA", bad_sent, roi])
        return sentSet


    #simple_verb_process('simple_agrmt_all.jsonl', paper_df, 1, "simple")
    csv_file = "combined_verb_list.csv"
    verbList = process_csv(csv_file)
    lineList = []
    numContext = 1
    sentSet = set()

    #['sentID', 'comparison', 'pairid', 'contextid', 'lemma', 'condition', 'pronoun', 'sentence', 'ROI']    
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