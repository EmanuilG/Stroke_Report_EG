# Stroke_Report_EG

Get data on stroke patients of a German stroke unit as csv-files, generate a customizable statistical report.

## A brief overview 

Get data on stroke patients of a stroke unit as csv-files, add three self-filled csv-files, run code in [Python](www.python.org),  [Pandas](https://pandas.pydata.org/), some [Powershell](https://en.wikipedia.org/wiki/PowerShell), [Pandoc Markdown](https://pandoc.org/), some [Latex](https://www.latex-project.org/) and generate a customizable statistical report. 

I am a physician and an amateur programmer. I wished to share the code and the way I did it. It may encourage others, whether programming physicians or professional programmers, to do similar - and much better - projects. 

## Rationale and description

In Germany there is a quality assurance program for stroke patients. Data for that program are gathered through a special module of every hospital IT-system. There is a fixed set of questions. The data are sent four times a year to an overseeing authority and the results are discussed. Of course we are encouraged to deliver a high level of care. 

As an attending neurologist at a stroke unit I wanted to answer additional quantitative questions about our patients and the care they receive. I was kindly granted access to the raw data of the quality assurance program as csv-files. 

The workflow is: 

1. Receive 4 csv-files (ischemic stroke, hemorrhagic stroke and two other files with administrative data)
2. Prepare 3 additional manually filled csv-files (which patients got referred to an endovascular treatment, which patients had echocardiography, why a door-to-needle-time of max 60 minutes was not achieved)
3. Rename the files to fixed standardized names
4. Convert the files to utf-8
5. Import all seven (4 + 3) csv-files into Pandas dataframes
6. Code answers in Pandas/Python
7. Export csv-files to be filled manually with information from the patient health records 
8. Export a markdown file with all necessary text and statistics 
9. Convert the markdown-file to pdf with Pandoc 

To understand my code fully you should be fluent in English and German and know a lot about care of stroke patients in German hospitals. If you do not speak German you can still inspect the structure of the code. The comments are in English. I am sorry I cannot share the patient data, so I cannot upload a report as a pdf-file. The structure of the csv-files you may receive from your IT-department may be different from that of my hospital. 

The files in that project are: 

1. sb.py: The main file 
2. metadata.yaml: The instructions for Pandoc
3. report.ps1: The workflow file with mixed PowerShell and Python code, it uses sb.py and the 2 rename python files.
4. RenameHi2bak.py: Rename outdated files and backing them up
5. RenameMSA2hi.py: Rename received csv-files to standard names

## If you plan a similar project 

I assume you are a programming stroke physician or a programmer in a German hospital with a stroke unit.  

Examine closely the csv-files you receive from your IT-department. You can use [Libre Office](https://de.libreoffice.org/) or a text editor with a csv-preview. I currently use [Visual Studio Code](https://code.visualstudio.com/) for programming and all my writing. Understand all the column headings, their meaning may not be obvious, there are abbreviated expressions like 'abstAufnIABild'. 

Ask your colleagues and your head of the department, what questions they might have. Ask yourself what you would like to know. 







