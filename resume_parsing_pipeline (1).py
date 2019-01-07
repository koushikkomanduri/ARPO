#!/usr/bin/env python
# coding: utf-8

# # <center>PHASE 1</center>
# 
# ---
# 
# 
# - Split data into columns - general details, education details, work experience detail
# 
# 
# - Verify split result with manual split *(around 100 resumes)*
# 
# 
# - Parse education detail column for valid 4 year degree and create a new column *(1 - valid, 0 - invalid)*
# 
# 
# - Use date_extractor library to extract dates in correct format from work experience column
# 
# ---

# ## Load all libraries

# In[1]:


# import libraries
import pandas as pd
import numpy as np


# ### <center>RESUME SPLIT</center>
# 
# ---

# #### Create labels for resume split

# In[3]:


# create labels

educationLabels = ['EDUCATION AND TRAINING', 'education:', 'Academic Background', 'education ', 
                   'Educational Learning', 'education', 'graduate']

workLabels = ['work experience', 'WORK HISTORY', 'professional experience', 'EMPLOYMENT History', 
              'Professional History', 'Experience Detail','Professional Summary', 'PROFESSIONAL PROFILE', 
              'Experience:', 'experience ', 'EMPLOYMENT', 'experience']


# #### Function for spliting data based on education and work experience

# In[4]:


# split function definition

def resumeSplit(df, filepath) :
    
    # create a copy
    data = df.copy()
    # create empty dataframe
    resumeDF = pd.DataFrame(columns = ['Candidate_Details', 'Education_Details', 'Work_Experience_Details'], 
                           index = range(0,len(data)+1)
                           )
    
    index = 0
    
    # loop through each resume
    for index in data.index.values :
      
        resume = data[index].lower()
        edSplit = []
    
        # loop through all education labels and split if match found
        for edLabel in educationLabels :
            edLabel = edLabel.lower()

            if edLabel in resume :
                edSplit = resume.split(edLabel, 1)
                break

        # create empty variables
        cd, ed, we = '','',''
        
        # if there is a education split
        if len(edSplit) != 0 :
        
            
            cd = edSplit[0]
            ed = edSplit[1]
            
            # loop through all work labels and split if match found
            for weLabel in workLabels :
                weLabel = weLabel.lower()
                if weLabel in edSplit[0] :
                    cd, we = edSplit[0].split(weLabel, 1)
                    break
                elif weLabel in edSplit[1] :
                    ed, we = edSplit[1].split(weLabel, 1)
                    break
                    
        # if there is no education split
        else :

            cd = resume
            
            # loop through all work labels and split if match found
            for weLabel in workLabels :
                weLabel = weLabel.lower()
            
                if weLabel in resume :
                    cd, we = resume.split(weLabel, 1)
                    break
        
        # create new row
        resumeDF.iloc[index].Candidate_Details = cd
        resumeDF.iloc[index].Education_Details = ed
        resumeDF.iloc[index].Work_Experience_Details = we
        
        index += 1

    ## update column name for prodigy
    resumeDF.rename(columns={'Candidate_Details' : 'Candidate_Details', 'Education_Details' : 'Education_Details',
       'Work_Experience_Details' : 'Text'}, inplace=True)
    
    ## write to disk
    resumeDF.to_csv(filepath, sep=',')


# #### Split resumes and save to csv

# In[5]:


# pass the csv to resumeSplit function

## all
resumeSplit(pd.read_csv('../data/resume_details.csv')['Text'], '../output/1_allSplit.csv')


# ### <center>EXTRACT EDUCATION LEVEL</center>
# ---

# #### Extract information for education and dummify

# In[287]:


data = pd.read_csv('../output/1_allSplit.csv')
data = data['Education_Details']


# #### Set labels for education

# In[288]:


degreeLabels = ['bachelor', 'master', 'b.a', 'm.a']


# #### Function for extracting education level (1 - valid, 0 - invalid)

# In[290]:


def dummifyEducation(df, filepath) :

    # create a copy
    data = df['Education_Details'].copy()

    data.fillna('0', inplace=True)
    
    # create empty dataframe
    educat = pd.DataFrame(columns =['EducationLevel'], 
                          index = range(0, len(data))
                         )
    
    ind = 0

    for index in data.index.values :

        edDetail = data[index].lower()

        for edLabel in degreeLabels :
            edLabel = edLabel.lower()
            
            educat.loc[ind].EducationLevel = 0
            
            if edLabel in edDetail :
                educat.loc[ind].EducationLevel = 1
                break
                
        ind = ind + 1  
        
    # add new row to dataframe
    educat = pd.concat([df,educat], axis = 1)
    
    ## write to disk
    educat.to_csv(filepath, sep=',')


# #### Extract education level and save to csv

# In[291]:


# pass the csv to dummifyEducation function
dummifyEducation(pd.read_csv('../output/1_allSplit.csv'), '../output/2_educat_level.csv')


# ### <center>EXTRACT YEARS OF EXPERIENCE</center>
# ---

# In[292]:


from date_extractor import extract_dates
import datetime

def yearsOfExpereince(df, filepath) :

    # create a copy
    data = df['Text'].copy()

    data.fillna('0', inplace=True)

    # create empty dataframe
    exp = pd.DataFrame(columns =['ExperienceLevel'], 
                          index = range(0, len(data))
                      )

    ind = 0

    for index in data.index.values :

        dates = extract_dates(data[index])

        dateList = []

        for date in dates :
                       
            date = date.strftime('%Y/%m/%d')
            
            if int(date[:4]) <= 2018 and int(date[:4]) > 1960 :
                dateList.append(date)
        
        exp.loc[ind].ExperienceLevel = 0
        if (int(max(dateList)[:4]) - int(max(dateList)[:4])) > 3 :
            exp.loc[ind].ExperienceLevel = 1
            break
                       
    ind += 1
    
    # add new row to dataframe
    exp = pd.concat([df, exp], axis = 1)
    
    ## write to disk
    exp.to_csv(filepath, sep=',')


# #### Extract years of experience and save to csv

# In[293]:


# pass the csv to dummifyEducation function
dummifyEducation(pd.read_csv('../output/1_allSplit.csv'), '../output/3_experience_level.csv')


# # <center>PHASE 2</center>
# 
# ---
# 
# 
# - Annotate job Overview column for distance threshold
# 
# 
# - Run spacy model on for distance threshold
# 
# 
# - Use Distance Matrix API to find distance between home and job locations
# 
# 
# - Create new column for valid address *(1 - valid, 0 - invalid)*
# 
# 
# - Look for Grammer API for evaluating cover letter
# 
# 
# - Create a new column for valid (present and well written) cover letter *(1 - valid, 0 - invalid)*
# 
# 
# - Parse resumes for valid clearance and create new column for valid Clearance *(1 - valid, 0 - invalid)*
# 
# 
# ---

# In[ ]:





# #### Convert prodigy/spacy output to dataframe

# In[192]:


import jsonlines
import json
from pandas.io.json import json_normalize

with jsonlines.open('../data/expDates1.jsonl') as reader:
#     df = pd.DataFrame(columns = ['text', 'tokens'], index = range(0, 49))
#     a = []
#     count = 0
#     for obj in reader :
#         a.append(json_normalize(obj))
#         df.iloc[count].text = a[count]['text']
#         df.iloc[count].tokens = pd.DataFrame.from_records(a[count]['tokens'])
#         count += 1
# #         print(pd.DataFrame.from_records(json_normalize(obj))
        
# df
    df = json.load(reader)
pd.DataFrame(df)


# In[186]:


x


# # <center>PHASE 3</center>
# 
# ---
# 
# 
# - Front End Development
# 
# 
# ---

# In[ ]:




