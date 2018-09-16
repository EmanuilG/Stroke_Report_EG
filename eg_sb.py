import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import os
import sys 
import re
import datetime
import locale
import statistics as stat 
from matplotlib2tikz import save as tikz_save
# Instead of plt.show(), invoke matplotlib2tikz by tikz_save('mytikz.tex')

start = datetime.datetime.now()


def df_to_md(df, file):
	''' takes a dataframe and a filename, 
	writes the dataframe to the file formatted as a markdown table
	'''
	# index=False removes the row labels	
	df.to_csv(file, encoding='utf-8', sep='|', index=False)
	# the 2nd line for the md-table
	# then add a | at the end of the line
	df2line = '\n' + '---' + '|---'*df.shape[1] + '\n'
	with open(file, 'r', encoding='utf-8') as f:
		f1 = f.read()
		f2 = f1.replace('\n', df2line, 1)
		f3 = f2.replace('\n', '|\n')
	with open(file, 'w', encoding='utf-8') as t:
		t.write(f3)

years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
yearsFmt = mdates.DateFormatter('%Y')

# to include all labels in the figures
plt.rcParams.update({'figure.autolayout': True})

# a method to insert the current date 
locale.setlocale(locale.LC_ALL, 'german_Germany')
now = datetime.datetime.now()
# the formal iso datetime timestamp
now_de_iso = now.strftime('%Y-%m-%d %H:%M:%S %A %B %Z')
# the common german date format
now_de_common = now.strftime('%d.%m.%Y')
# the month 
now_de_month = now.strftime('%B')


# read the csv files
hi = pd.read_csv('hi.csv', sep=';')
heb = pd.read_csv('heb.csv', sep=';')
vf = pd.read_csv('vf.csv', sep=';')
icb = pd.read_csv('icb.csv', sep=';')


# data on TTE and TEE
te = pd.read_csv('tte_tee.csv', sep=';')

# notes on Lyse > 60 min
lyno = pd.read_csv('falln_lyse_notes.csv', sep=';')

# data on transportation of patients for mechanical thrombectomy
mech_thromb = pd.read_csv('mt_transport.csv', sep=';')

# filter for the strokes and the completed QS-Bogen
# vf1 = vf[(vf['Modulkurz'] == 'Q801HE') & ((vf['Statuskurz'] == 'Export') | (vf['Statuskurz'] == 'OK'))]
# i used the filter Statuskurz == 'Export', it failed because i had a lot with 'OK', i then filtered only according to Modulkurz and fixed the problem. 
# vf1 = vf[(vf['Modulkurz'] == 'Q801HE')]
# Then i realized that any filtering is not necessary 02.06.2018 and i coded:
vf1 = vf

# all patients with stroke regardless of the state of the QS-Bogen
vf_allstroke1 = vf[(vf['Modulkurz'] == 'Q801HE')]
vf_allstroke = vf_allstroke1['Vorgangsnummer'].count()

# keep the needed columns
vf2 = vf1[['Vorgangsnummer', 'Fallnummer', 'Geburtsdatum', 'Aufnahmedatum', 'Entlassdatum']]

# rename the column of vf3 from Vorgangsnummer to Vorgangsnr to prepare the merging
# hi, heb and icb have already Vorgangsnr
vf3 = vf2.rename(columns={'Vorgangsnummer' : 'Vorgangsnr'})

# sort the dataframe according to Vorgangsnr and reset the index of the four dataframes 
# vf3
vf3 = vf3.sort_values(by='Vorgangsnr')
vf3 = vf3.reset_index(drop=True)
# hi
hi = hi.sort_values(by='Vorgangsnr')
hi = hi.reset_index(drop=True)
# heb
heb = heb.sort_values(by='Vorgangsnr')
heb = heb.reset_index(drop=True)
# icb
icb = icb.sort_values(by='Vorgangsnr')
icb = icb.reset_index(drop=True)

# merging gives the intersection of rows and union of columns

# merging in 2 steps hi and vf3, then the merged dataframe with heb
hi1 = pd.merge(hi, vf3, on='Vorgangsnr')
hi2 = pd.merge(hi1, heb, on='Vorgangsnr')

# 02.06.2018 look for discharge dead
# hi2['SCRANK_E']==6.0

# merge data on TTE and TEE 
hi2 = pd.merge(hi2, te, on='Fallnummer', how='outer')

# merge data on mechanical thrombectomy
hi2 = pd.merge(hi2, mech_thromb, on='Fallnummer', how='outer')

# merge data on lyse > 60 min with notes
hi2 = pd.merge(hi2, lyno, on='Fallnummer', how='outer')

# merging in 2 steps icb and vf3, then the merged dataframe with heb
icb1 = pd.merge(icb, vf3, on='Vorgangsnr')
icb2 = pd.merge(icb1, heb, on='Vorgangsnr')

# # # # # # # # # 
# ischemic stroke 
# # # # # # # # # 

# change dtype to datetime
hi2['Geburtsdatum'] = pd.to_datetime(hi2['Geburtsdatum'], format="%d.%m.%Y")
hi2['Aufnahmedatum'] = pd.to_datetime(hi2['Aufnahmedatum'], format="%d.%m.%Y %H:%M")
hi2['Entlassdatum'] = pd.to_datetime(hi2['Entlassdatum'], format="%d.%m.%Y %H:%M")

# age in years 
hi2['alter']
# time in hospital 
hi2['vwDauer']
# how many patients - ischemic stroke 
hi2_count = hi2['Vorgangsnr'].count()
# Lyse-patients absolute, 2 means Lyse
hi2_lyse = hi2['SYSTTHLYSE'].value_counts()[2]
# Lyse-patients percent 
hi2_lyse_pc = round(hi2_lyse * 100/hi2_count, 1)

# Aufnahme-Lyse-Median
hi2_lyse_adm_ly_median = round(hi2['abstAufnThLyse'].median(), 0)

# Aufnahme-Lyse-Zeit <= 60 min (Prozentsatz)
hi2_lyse_60_pc1 = hi2[hi2['abstAufnThLyse'] <= 60.0]['abstAufnThLyse'].count()*100/hi2_lyse
hi2_lyse_60_pc = round(hi2_lyse_60_pc1, 1)

# numbers of all patients with Aufnahme-Lyse-Zeit > 60 min as a list 
hi2_lyse_ue60 = list(hi2.loc[(hi2['abstAufnThLyse'] > 60.0), 'Fallnummer'])


# dataframe of all patients with Aufnahme-Lyse-Zeit > 60 min with time columns and notes 
# this dataframe must get into the report1.md
hi2_lyse_ue60_df = hi2.loc[(hi2['abstAufnThLyse'] > 60.0), ['Fallnummer','Aufnahmedatum', 'abstAufnIABild', 'abstIABildThLyse', 'abstAufnThLyse', 'lyse_notes']]

df_to_md(hi2_lyse_ue60_df, 'ueber60warum.md')

# dataframe of all patients with Aufnahme-Lyse-Zeit > 60 min with no entry in notes
hi2_lyse_ue60_no_note = hi2_lyse_ue60_df.loc[hi2_lyse_ue60_df['lyse_notes'].isnull(), ['Fallnummer', 'lyse_notes']]

# create a file with all patients with Aufnahme-Lyse-Zeit > 60 min with no entry in notes
# when I fill the column of lyse_notes I add the rows to the file falln_lyse_notes.csv
hi2_lyse_ue60_no_note.to_csv('falln_lyse_notes_out.csv', sep=';', index=False)

# 01.09.2018 MH wished a table with Lyse-patients and the times 
# A dataframe with all Lyse-patients and the times
hi2_ld_all = hi2.loc[hi2['SYSTTHLYSE']==2, ['Fallnummer', 'abstAufnIABild', 'abstIABildThLyse', 'abstAufnThLyse']] 
# add a column with blank cells 
# hi2_ld_all = hi2_ld_all.assign(lyse_notes = "")


# create file with a markdown table of the dataframe hi2_ld_all
df_to_md(hi2_ld_all, 'Lyse_Zeiten.md')
# create a csv file with the dataframe hi2_ld_all
hi2_ld_all.to_csv('Lyse_Zeiten.csv', index=False)


# Experimental: Correlation of datetime and door to needle time
# hi2_ld = hi2.loc[hi2['SYSTTHLYSE']==2, ['abstAufnThLyse', 'Aufnahmedatum']] 
hi2_ld1 = hi2.loc[hi2['SYSTTHLYSE']==2, ['abstAufnThLyse', 'Aufnahmedatum']] 

# hi2_ld2 = hi2_ld1.set_index('Aufnahmedatum')

# hi2_ld1['Wochentag_Name'] = hi2_ld1['Aufnahmedatum'].dt.weekday_name
hi2_ld1['Wochentag_Zahl'] = hi2_ld1['Aufnahmedatum'].dt.weekday
hi2_ld1['Datum'] = hi2_ld1['Aufnahmedatum'].map(lambda x: x.strftime('%Y-%m-%d'))
hi2_ld1['Uhrzeit'] = hi2_ld1['Aufnahmedatum'].dt.hour

# hi2_ld1 is a DataFrame with all Lyse-patients listing the Aufnahme-Lyse-Zeit, Wochentag_Zahl, Datum and Uhrzeit. I want a group for patients normal working hours and another for patients outside normal working hours. I want to examine whether there is a difference in the Aufnahme-Lyse-Zeit between the two groups

# Feiertage in Hessen 2018
feiertage2018 = ['2018-01-01', '2018-03-30', '2018-04-02', '2018-05-01', '2018-05-10', '2018-05-21', '2018-05-31', '2018-10-03', '2018-12-25', '2018-12-26']

# hi2_ld2 is a Dataframe with the Lyse-patients in normal working hours
hi2_ld2 = hi2_ld1.loc[(hi2_ld1['Uhrzeit']<17) & (hi2_ld1['Uhrzeit']>7) & (hi2_ld1['Wochentag_Zahl']<5) & (hi2_ld1['Datum'].map(lambda x: x not in feiertage2018))] 

# hi2_ld2_indexlist is a list with the index of the the Lyse-patients in normal working hours. I need it to subtract the rows from the DataFrame with all Lyse-patients
hi2_ld2_indexlist = list(hi2_ld2.index)

# hi2_ld3 is a Dataframe with the Lyse-patients outside normal working hours
hi2_ld3 = hi2_ld1.drop(hi2_ld2_indexlist)

hi2_ld2_stat = hi2_ld2['abstAufnThLyse'].describe()

hi2_ld3_stat = hi2_ld3['abstAufnThLyse'].describe()

hi2_ld2_stat_count = round(hi2_ld2_stat['count'], 0)
hi2_ld2_stat_max = round(hi2_ld2_stat['max'], 0)
hi2_ld2_stat_75 = round(hi2_ld2_stat['75%'], 0)
hi2_ld2_stat_50 = round(hi2_ld2_stat['50%'], 0)
hi2_ld2_stat_25 = round(hi2_ld2_stat['25%'], 0)
hi2_ld2_stat_min = round(hi2_ld2_stat['min'], 0)

hi2_ld3_stat_count = round(hi2_ld3_stat['count'], 0)
hi2_ld3_stat_max = round(hi2_ld3_stat['max'], 0)
hi2_ld3_stat_75 = round(hi2_ld3_stat['75%'], 0)
hi2_ld3_stat_50 = round(hi2_ld3_stat['50%'], 0)
hi2_ld3_stat_25 = round(hi2_ld3_stat['25%'], 0)
hi2_ld3_stat_min = round(hi2_ld3_stat['min'], 0)

# Aufnahme-Bildgebung-Zeit (Median)
hi2_adm_im_median = round(hi2['abstAufnIABild'].median(), 0)

# all patients with imaging in BH
hi2_im = hi2['abstAufnIABild'].count()

# all patients with imaging in BH with Aufnahme-Bildgebung < 30 min 
hi2_adm_im_30 = hi2[hi2['abstAufnIABild'] <30.0]['abstAufnIABild'].count()

# numbers of all patients with imaging in BH with Aufnahme-Bildgebung > 30 min 
hi2_adm_im_ue30 = list(hi2.loc[(hi2['abstAufnIABild'] >=30.0), 'Fallnummer'])

# percentage of patients with Aufnahme-Bildgebung < 30 min 
hi2_adm_im_30_pc = round(hi2_adm_im_30*100/hi2_im, 0)

# all anticoagulated patients 
hi2_oak = hi2.loc[(hi2['VANTIKOA'] > 0), 'VANTIKOA'].count()

# all patients with a large vessel occlusion 
hi2_lvo = hi2.loc[(hi2['GEFVERSCHL'] > 0), 'GEFVERSCHL'].count()

# Fallnummer of patients with a large vessel occlusion
hi2_lvo_fn = list(hi2.loc[(hi2['GEFVERSCHL'] > 0), 'Fallnummer'])

# all patients with a large vessel occlusion and transport to Fulda
hi2_lvo_transp1 = hi2.loc[((hi2['GEFVERSCHL'] > 0) & (hi2['w_verlegt'] > 0)), 'Fallnummer']

hi2_lvo_transp = hi2_lvo_transp1.count()

# NIHSS statistics 
nih_stat = hi2['SCNIHSSA'].describe()
nih_stat_mean = round(nih_stat['mean'], 0)
nih_stat_median = round(nih_stat['50%'], 0)
nih_stat_max = round(nih_stat['max'], 0)

# all palliative patients
hi2_pall1 = hi2.loc[(hi2['VERFUEGUNG']>0), 'Vorgangsnr']
hi2_pall = hi2_pall1.count()

# Median age of palliative patients 
hi2_pall_median_age = round(hi2.loc[(hi2['VERFUEGUNG']>0), 'alter'].median(), 1)

# Median mRS of palliative patients at admission 
hi2_pall_median_mrs_a = round(hi2.loc[(hi2['VERFUEGUNG']>0), 'SCRANK_A'].median(), 1)

# all patients with critical care  
hi2_cc = hi2.loc[(hi2['INTENSIV'] > 0), 'INTENSIV'].count()

# all ischemic stroke who got a TTE
hi2_tte = hi2.loc[(hi2['TTE'] == 1.0), 'TTE'].count()

# percentage of all ischemic stroke who got a TTE
hi2_tte_pc = round(hi2_tte*100/hi2_count, 1)

# all ischemic stroke who got a TTE
hi2_tee = hi2.loc[(hi2['TEE'] == 1.0), 'TEE'].count()

# percentage of all ischemic stroke who got a TTE
hi2_tee_pc = round(hi2_tee*100/hi2_count, 1)

# find Fallnummer of patients with no entry in TTE 
hi2_fd = hi2.loc[(hi2['TTE'].isnull()), 'Fallnummer']

# find Fallnummer of patients with Lyse > 60 min and no entry in notes
# hi2_ly60fn = hi2.loc[(hi2['TTE'].isnull()), 'Fallnummer']

# how many ischemic stroke patients died 
hi2_rs6 = hi2[hi2['SCRANK_E'] == 6.0]['SCRANK_E'].count()

# Fallnummer of patients who died 
hi2_rs6_fn = list(hi2.loc[(hi2['SCRANK_E'] == 6.0), 'Fallnummer'])

# Percentage of ischemic stroke patients who died 
hi2_rs6_pc = round(hi2_rs6*100/hi2_count, 1)

# Fallnummer of patients who died and were in palliation
hi2_rs6_pall = hi2.loc[(hi2['SCRANK_E'] == 6.0) & (hi2['VERFUEGUNG']>0), 'Fallnummer']

# Fallnummer of patients who died and were not in palliation
hi2_rs6_npall = hi2.loc[((hi2['SCRANK_E'] == 6.0) & (hi2['VERFUEGUNG']==0)), 'Fallnummer']

# Fallnummer of patients with no entry in 'VERFUEGUNG'
hi2_verf_noentry = hi2.loc[hi2['VERFUEGUNG'].isnull(), 'Fallnummer']



######################
### Hemorrhagic stroke 
######################


# change dtype to datetime
icb2['Geburtsdatum'] = pd.to_datetime(icb2['Geburtsdatum'], format="%d.%m.%Y")
icb2['Aufnahmedatum'] = pd.to_datetime(icb2['Aufnahmedatum'], format="%d.%m.%Y %H:%M")
icb2['Entlassdatum'] = pd.to_datetime(icb2['Entlassdatum'], format="%d.%m.%Y %H:%M")
# age in years 
icb2['alter']
# time in hospital 
icb2['vwDauer']

# how many patients - hemorrhagic stroke 
icb2_count = icb2['Vorgangsnr'].count()
# all anticoagulated patients 
icb2_oak = icb2.loc[(icb2['VANTIKOA'] > 0), 'VANTIKOA'].count()
# how many hemorrhagic stroke patients died 
icb2_rs6 = icb2[icb2['SCRANK_E'] == 6.0]['SCRANK_E'].count()
# all palliative patients
icb2_pall1 = icb2.loc[(icb2['VERFUEGUNG']>0), 'Vorgangsnr']
icb2_pall = icb2_pall1.count()
# all patients with critical care  
icb2_cc = icb2.loc[(icb2['INTENSIV'] > 0), 'INTENSIV'].count()


# ###################################################
# ######### A first attempt at visualization ########
# ###################################################

# # Alter with histogram, not so useful 
# # fig, ax = plt.subplots()
# # age_hi = hi2['alter']
# # ax = age_hi.plot.hist(bins=list(range(110)))
# # ax.set_title('Alter der Hirninfarkt-Patienten')
# # ax.set_xlabel('Jahre')
# # ax.set_ylabel('Anzahl von Patienten')
# # # ax.set_yticks(range(hi2_lyse))
# # ax.legend('')
# # plt.show()


# # start of Alter 
# z2 = hi2['alter']
# fig, ax = plt.subplots()
# # to make a figure with more Axes you need to set a number of rows and columns, then you have to set labels, titles for each of the Axes
# # fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))
# z2.plot(kind='box', whis='range', showbox=True, showcaps=True)
# ax.set_title('Alter der Hirninfarkt-Patienten')
# ax.set_ylabel('Jahre')
# ax.set_xlabel('')
# ax.set_xticklabels('')
# ax.set_ylim(ymin=20, ymax=110)

# ax.annotate('Maximum', xy=(1.05, z2.max()), xytext=(1.2, z2.max()+5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
# ax.annotate('Median', xy=(1.07, z2.median()), xytext=(1.25, z2.median()+5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
# ax.annotate('0,75-Perzentil', xy=(1.07, np.percentile(z2, 75)), xytext=(1.25, np.percentile(z2, 75)+5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
# ax.annotate('0,25-Perzentil', xy=(1.07, np.percentile(z2, 25)), xytext=(1.25, np.percentile(z2, 25)+5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
# ax.annotate('Minimum', xy=(1.05, z2.min()), xytext=(1.2, z2.min()+5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))

# ax.annotate(int(round(np.percentile(z2, 100))), xy=(0.95, np.percentile(z2, 100)), xytext=(0.8, np.percentile(z2, 100)-5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
# ax.annotate(int(round(np.percentile(z2, 75))), xy=(0.93, np.percentile(z2, 75)), xytext=(0.75, np.percentile(z2, 75)-5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
# ax.annotate(int(round(np.percentile(z2, 50))), xy=(0.93, np.percentile(z2, 50)), xytext=(0.75, np.percentile(z2, 50)-5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
# ax.annotate(int(round(np.percentile(z2, 25))), xy=(0.93, np.percentile(z2, 25)), xytext=(0.75, np.percentile(z2, 25)-5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
# ax.annotate(int(round(np.percentile(z2, 0))), xy=(0.95, np.percentile(z2, 0)), xytext=(0.8, np.percentile(z2, 0)-5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))

# plt.savefig('Alter1.png')

# # end of Alter



# start of Lyse 
# create a series with only the Lyse patients
hi2_lyse_Series1 = hi2.loc[(hi2['abstAufnThLyse'] >0), ['abstAufnThLyse']]
hs = pd.Series(hi2_lyse_Series1['abstAufnThLyse'])
fig, ax = plt.subplots()

hs.plot(kind='box', whis='range', showbox=True, showcaps=True)
# ax.boxplot(hs, whis='range')
ax.set(title='Aufnahme - Lyse - Zeit      Lysen: ' +  str(hs.count()), ylabel='Minuten', xlabel='')
ax.set_xticklabels('')
ax.text(0.55, 62, 'Obergrenze = 60 min')
ax.axhline(y=60, ls='--', color='red')
ax.set_ylim((hs.min()-10),(hs.max()+10))

ax.annotate('Maximum', xy=(1.05, hs.max()), xytext=(1.2, hs.max()+5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
ax.annotate('Median', xy=(1.07, hs.median()), xytext=(1.25, hs.median()+5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
ax.annotate('0,75-Perzentil', xy=(1.07, np.percentile(hs, 75)), xytext=(1.25, np.percentile(hs, 75)+5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
ax.annotate('0,25-Perzentil', xy=(1.07, np.percentile(hs, 25)), xytext=(1.25, np.percentile(hs, 25)+5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
ax.annotate('Minimum', xy=(1.05, hs.min()), xytext=(1.2, hs.min()+5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))

ax.annotate(int(round(np.percentile(hs, 100))), xy=(0.95, np.percentile(hs, 100)), xytext=(0.8, np.percentile(hs, 100)-5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
ax.annotate(int(round(np.percentile(hs, 75))), xy=(0.93, np.percentile(hs, 75)), xytext=(0.75, np.percentile(hs, 75)-5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
ax.annotate(int(round(np.percentile(hs, 50))), xy=(0.93, np.percentile(hs, 50)), xytext=(0.75, np.percentile(hs, 50)-5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
ax.annotate(int(round(np.percentile(hs, 25))), xy=(0.93, np.percentile(hs, 25)), xytext=(0.75, np.percentile(hs, 25)-5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
ax.annotate(int(round(np.percentile(hs, 0))), xy=(0.95, np.percentile(hs, 0)), xytext=(0.8, np.percentile(hs, 0)-5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
plt.tight_layout(pad=2, w_pad=25, h_pad=35)
fig.savefig('Aufnahme_Lyse_fig2.png')


# start of Aufnahme - Bildgebung 
hi_im_all_1 = hi2.loc[hi2['abstAufnIABild']>0, 'abstAufnIABild']
hi_im_all = pd.Series(hi_im_all_1)


fig, ax = plt.subplots()
hi_im_all.plot(kind='box', whis='range', showbox=True, showcaps=True)
ax.set_title('Aufnahme - Bildgebung, Bildgebungen: '+ str(hi_im_all.count()))
ax.set_ylabel('Minuten')
ax.set_xlabel('')
ax.set_xticklabels('')
ax.set_ylim(ymin=0, ymax=hi_im_all.max() + 30)
ax.text(0.51, 55, 'Obergrenze = 30 min')
ax.axhline(y=30, ls='--', color='red')

ax.annotate('Maximum', xy=(1.05, hi_im_all.max()), xytext=(1.2, hi_im_all.max()+5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
ax.annotate('Median', xy=(1.07, hi_im_all.median()), xytext=(1.25, hi_im_all.median()+5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
ax.annotate('0,75-Perzentil', xy=(1.07, np.percentile(hi_im_all, 75)), xytext=(1.25, np.percentile(hi_im_all, 75)+5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
ax.annotate('0,25-Perzentil', xy=(1.07, np.percentile(hi_im_all, 25)), xytext=(1.25, np.percentile(hi_im_all, 25)+5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
ax.annotate('Minimum', xy=(1.05, hi_im_all.min()), xytext=(1.2, hi_im_all.min()+5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))

ax.annotate(int(round(np.percentile(hi_im_all, 100))), xy=(0.95, np.percentile(hi_im_all, 100)), xytext=(0.8, np.percentile(hi_im_all, 100)-5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
ax.annotate(int(round(np.percentile(hi_im_all, 75))), xy=(0.93, np.percentile(hi_im_all, 75)), xytext=(0.75, np.percentile(hi_im_all, 75)-5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
ax.annotate(int(round(np.percentile(hi_im_all, 50))), xy=(0.93, np.percentile(hi_im_all, 50)), xytext=(0.75, np.percentile(hi_im_all, 50)-5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
ax.annotate(int(round(np.percentile(hi_im_all, 25))), xy=(0.93, np.percentile(hi_im_all, 25)), xytext=(0.75, np.percentile(hi_im_all, 25)-5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))
ax.annotate(int(round(np.percentile(hi_im_all, 0))), xy=(0.95, np.percentile(hi_im_all, 0)), xytext=(0.8, np.percentile(hi_im_all, 0)-5), arrowprops=dict(facecolor='grey', shrink=0.05, width=0.1, headwidth=6))

plt.savefig('Aufn_Bild1.png')

# end of Aufnahme-Bildgebung





# create a pd.Series out of the two columns
# hi2_wb1 = pd.Series(list(hi2_wb['abstAufnThLyse']), index=hi2_wb['Aufnahmedatum'])

# myDates = hi2_wb['Aufnahmedatum']
# myValues = hi2_wb['abstAufnThLyse']

# fig, ax = plt.subplots()
# ax.(myDates,myValues)
# myFmt = DateFormatter("%d.%m.%Y")
# ax.xaxis.set_major_formatter(myFmt)
# ## Rotate date labels automatically
# plt.show()

# plt.figure()
# plt.style.use('fast')
# plt.text(45, 0.2, 'Höchstzeit = 60 min')
# ax = hi2_wb1.plot(kind='barh', color='#808080')
# # ax = hi2_wb1.plot(kind='box', color='#808080')
# ax.axvline(x=60, linewidth=1, color = 'r')
# # plt.grid(True)
# # labels = ax.get_xticklabels()
# # plt.setp(labels, rotation=45, horizontalalignment='right')
# # plt.xlabel('Aufnahmedatum und -uhrzeit')
# plt.xlabel('Aufnahme - Lyse in min')
# plt.title('Aufnahme - Lyse - Zeit')
# # i can save as tikz, it did not work well, parts of the figure were cut. Saving to pgf had the same effect. 
# # tikz_save('Aufnahme_Lyse_fig1.tex')
# # plt.savefig('Aufnahme_Lyse_fig1.png')
# # plt.show()




# the file with the picture code is opened and two changes are made with regex, the first is to eliminate the lines that begin with % and the second is to set \tick right. See next line: 
# i have to use \\\\ before t to get \tick and noch \t meaning tab 
# with open('Altersgruppen.tex', 'r') as myfile:
#     Altersgruppen_fig1 = myfile.read();	Altersgruppen_fig2 = re.sub('^%.*?\n', '', Altersgruppen_fig1)
#     Altersgruppen_fig3 = \
# 	re.sub('tick align', 'xticklabel={$\mathsf{\pgfmathprintnumber{\\\\tick}}$},\nyticklabel={$\mathsf{\pgfmathprintnumber{\\\\tick}}$},\ntick align', Altersgruppen_fig2)
# end of age groups 


# I can format the output
bericht1 = '''# Einleitung 

In den Qualitätssicherungs-Bögen (QS-Bögen) unserer Schlaganfallpatienten erfassen wir viele wertvolle Daten zur Demographie, Diagnostik und Behandlung. Die Abteilung für das QS-Management schickt mir an jedem Monatsanfang die Daten der QS-Bögen in Form von csv-Dateien. Diese Daten betreffen die Patienten, die wir seit dem Beginn des laufenden Jahres behandelt haben. 

Ein eigens geschriebenes Programm in der Programmiersprache Python (plus Datenanalyse-Modul Pandas) bereitet diese Daten auf. 

Dieser Bericht will Aspekte unserer Patienten und deren Versorgung darstellen. Er erscheint alle drei Monate, parallel zum QS-Monitor Saatmann-Tool. Durch den eigenen Blick auf unsere Daten können wir Fragen beantworten, die zwar kein unmittelbarer Gegenstand der Qualitätssicherung sind, aber uns dennoch interessieren. Der Bericht wendet sich an den Chefarzt und die Oberärztinnen/Oberärzte unserer Klinik. 

Emanuil Giuris

# Daten vom 01.01.2018 bis zum 31.08.2018

Letzte Aktualisierung: {}

Anzahl aller Schlaganfallpatienten: {}  
Anzahl der ischämischen Schlaganfallpatienten mit komplettiertem QS-Bogen: {}  
Anzahl der hämorrhagischen Schlaganfallpatienten mit komplettiertem QS-Bogen: {}  

## Hirninfarkt/TIA

Die {} komplettierten QS-Bögen der ischämischen Schlaganfallpatienten zeigen:

- Lyse bekamen: {} Patienten ({} % aller Patienten)
- Aufnahme-Lyse-Zeit (Medianwert): {} min
- Aufnahme-Lyse-Zeit bis 60 min: {} % aller Lysen
- Aufnahme-Bildgebung-Zeit (Medianwert): {} min
- Aufnahme-Bildgebung-Zeit < 30 min: {} % aller Patienten
- Vorbehandelt mit Antikoagulanzien waren: {} Patienten
- NIHSS-Mittelwert (arithmetisches Mittel): {} Punkte
- NIHSS-Medianwert: {} Punkte
- Transthorakale Echokardiographie bekamen {} Patienten ({} % aller Patienten)
- Transösophageale Echokardiographie bekamen {} Patienten ({} % aller Patienten)
- Verschluss eines großen Hirngefäßes: {} Patienten, verlegt wurden {} Patienten
- Intensivmedizinisch behandelt wurden: {} Patienten
- Es sind {} Patienten verstorben ({} % aller Patienten)
- Rein palliativ wurden {} Patienten behandelt
- Medianwert des Alters der Palliativ-Patienten: {} Jahre
- Medianwert des mRS der Palliativ-Patienten bei Aufnahme: {} Punkte

### Aufnahme-Lyse-Zeit über 60 min 

ueber60warum


### Aufnahme-Lyse-Zeit in und außerhalb der normalen Arbeitszeit 

Parameter | In normaler Arbeitszeit | Außerhalb normaler Arbeitszeit|
---------|----------|---------|
 Anzahl (Patienten) | {} | {} |
 Maximum (min) | {} | {} |
 0,75-Perzentil (min)  | {} | {} |
 Median  (min)| {} | {} |
 0,25-Perzentil  (min)| {} | {} |
 Minimum  (min)| {} | {} |

Aufnahme-Lyse-Zeit und deren [Fünf-Punkte-Zusammenfassung](https://de.wikipedia.org/wiki/Boxplot): Maximum, Minimum, Median (oder 0,5-Perzentil, der Wert oberhalb dessen die Hälfte der gemessenen Werte liegt), 0,75-Perzentil (unterhalb dessen liegen 75 \% aller gemessenen Werte), 0,25-Perzentil. 

### Alle Lyse-Patienten 

allelysepatienten


## Hirnblutung

Die {} komplettierten QS-Bögen der hämorrhagischen Schlaganfallpatienten zeigen:

- Vorbehandelt mit Antikoagulanzien waren: {} Patienten
- Es sind {} Patienten verstorben
- Rein palliativ wurden {} Patienten behandelt
- Intensivmedizinisch behandelt wurden: {} Patienten

## Fallnummern

In diesen Fällen weichen wir von den Vorgaben ab: 

Fallnummern der Patienten mit Aufnahme-Bildgebung-Zeit > 30 min: 
{}

Fallnummern der Patienten mit Aufnahme-Lyse-Zeit > 60 min: 
{}

Fallnummern der Patienten mit Hirninfarkt, die verstorben sind: 
{}

Fallnummern der Patienten mit Verschluss eines großen Gefäßes
{}

## Graphiken 


'''.format(now_de_common, vf_allstroke, hi2_count, icb2_count, hi2_count, hi2_lyse, hi2_lyse_pc, hi2_lyse_adm_ly_median, hi2_lyse_60_pc, hi2_adm_im_median, hi2_adm_im_30_pc, hi2_oak, nih_stat_mean, nih_stat_median, hi2_tte, hi2_tte_pc, hi2_tee, hi2_tee_pc, hi2_lvo, hi2_lvo_transp, hi2_cc, hi2_rs6, hi2_rs6_pc, hi2_pall, hi2_pall_median_age, hi2_pall_median_mrs_a, hi2_ld2_stat_count, hi2_ld3_stat_count, hi2_ld2_stat_max, hi2_ld3_stat_max, hi2_ld2_stat_75, hi2_ld3_stat_75, hi2_ld2_stat_50, hi2_ld3_stat_50, hi2_ld2_stat_25, hi2_ld3_stat_25, hi2_ld2_stat_min, hi2_ld3_stat_min, icb2_count, icb2_oak, icb2_rs6, icb2_pall, icb2_cc, hi2_adm_im_ue30, hi2_lyse_ue60, hi2_rs6_fn, hi2_lvo_fn)


# writes the report text 
with open('report1.md', 'w', encoding='utf-8') as f:
	f.write(str(bericht1))
	
# gets the lyse > 60 table from the external file 
with open('ueber60warum.md', 'r', encoding='utf-8') as u6:
	u6_1 = u6.read()
	
# inserts the lyse > 60 table into the report1 replacing the placeholder word ueber60warum - in 2 steps
with open('report1.md', 'r', encoding='utf-8') as f:
	f1 = f.read()
	f2 = re.sub(r'ueber60warum', u6_1, f1)

with open('report1.md', 'w', encoding='utf-8') as r:
		r.write(f2)

# gets all lyse patients from the external file 
with open('Lyse_Zeiten.md', 'r', encoding='utf-8') as lz:
	lz_1 = lz.read()

# inserts all lyse patients into the report1 replacing the placeholder word allelysepatienten - in 2 steps
with open('report1.md', 'r', encoding='utf-8') as f:
	f1 = f.read()
	f2 = re.sub(r'allelysepatienten', lz_1, f1)

with open('report1.md', 'w', encoding='utf-8') as r:
		r.write(f2)

# inserts the latex code for the figures into the report
with open('Graphiken.md', 'r', encoding='utf-8') as graphiken1:
	graphiken = graphiken1.read()
	with open('report1.md', 'a', encoding='utf-8') as report:
		report.write(str(graphiken))

# change the decimal sign from point to comma 
# change the lyse table headers to human readable text 
with open('report1.md', 'r', encoding='utf-8') as f:
	f1 = f.read()
	f2 = re.sub(r'(\d)\.(\d)( |\|)', '\g<1>,\g<2>\g<3> ', f1)
	f2 = re.sub(r'abstAufnIABild', 'Aufnahme--Bild (min)', f2)
	f2 = re.sub(r'abstIABildThLyse', 'Bild--Lyse', f2)
	f2 = re.sub(r'abstAufnThLyse', 'Aufnahme--Lyse', f2)
	f2 = re.sub(r'lyse_notes', 'Bemerkungen', f2)
	f2 = re.sub(r'(\d\d:\d\d):\d\d', '\g<1>', f2)
	f2 = re.sub(r'(\d),0', '\g<1> ', f2)
	f2 = re.sub(r'Aufnahmedatum', 'Aufnahme', f2)

with open('report1.md', 'w', encoding='utf-8') as r:
	r.write(f2)

# updates the date of the report and the month of the report
with open('metadata_report1.yaml', 'r', encoding='utf-8') as m1:
	m2 = m1.read()
	m3 = re.sub(r'\d\d\.\d\d\.2018', now_de_common, m2)
	m4 = re.sub(r'(date: )\w{1,12}( 2018)', '\g<1>{}\g<2>'.format(now_de_month), m3)

with open('metadata_report1.yaml', 'w', encoding='utf-8') as m1:
	m1.write(m4)

# write a file with Fallnummer of patients with no entry on TTE
with open('tte_tee_out.csv', 'w', encoding='utf-8') as fn1:
	fn1.write(hi2_fd.to_string())

with open('tte_tee_out.csv', 'r', encoding='utf-8') as fn1:
	fn2 = fn1.read()
	fn3 = re.sub(r'\n\d{1,5}\s{1,9}', '\n', fn2)
	fn4 = re.sub(r'(\d{1,9})\n', '\g<1>;;\n', fn3)
	fn5 = re.sub(r'^\d{1,9}\s{1,9}', '', fn4)
			
with open('tte_tee_out.csv', 'w', encoding='utf-8') as fn:
	fn.write('Fallnummer;TTE;TEE\n'+fn5+';;')


end = datetime.datetime.now()

print(end-start)

