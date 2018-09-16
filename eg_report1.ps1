# Select code and press F8



# 1. Rename old hi.csv and such and archive them with RenameHi2bak
python .\RenameHi2bak.py \


# 2. Rename new files with RenameMSA2hi and convert to  utf-8 
python .\RenameMSA2hi.py;gc .\heb1.csv | sc heb.csv -Encoding UTF8;gc .\hi1.csv | sc hi.csv -Encoding UTF8;gc .\icb1.csv | sc icb.csv -Encoding UTF8;gc .\vf1.csv | sc vf.csv -Encoding UTF8; Remove-Item .\heb1.csv, .\hi1.csv, .\icb1.csv, .\vf1.csv


# 3. Change manually the date in the name of the pdf-file below 


# run sp.py, run pandoc, run pdf-viewer 
python .\sb.py;pandoc.exe -f markdown -t latex -o Bericht_Schlaganfall_20180831.pdf -V documentclass=scrartcl -V papersize=a4 -V fontsize=11pt -V geometry:margin=2cm --toc -V colorlinks -V toccolor=blue -N .\report1.md .\metadata_report1.yaml; SumatraPDF.exe '.\Bericht_Schlaganfall_20180831.pdf'

