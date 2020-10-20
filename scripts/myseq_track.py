#Track miseq directory#!/usr/bin/python
import os
from collections import defaultdict, OrderedDict
import sys
import argparse
import subprocess
import sys
import glob
import pandas as pd
import logging
import csv
import shutil
import smtplib
import mimetypes
from email.message import EmailMessage
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

VERSION = '0.1'
CITATION = 'Data_tracker_Subin_Gireesh'
#Traverse directory tree


def append_files(inputpaths,outputpaths):
    new_list = []
    exclude_list = ['Config', 'Data', 'InterOp', ' Recipe', 'Thumbnail_Images', 'Logs']
    
    for (path,dirs,files) in os.walk(inputpaths):

     for dir in exclude_list:
        if dir in dirs:
           dirs.remove(dir)

     for file in files:
        if file.startswith("SampleSheet.csv"):
          #new_list.append(file)
          new_list.append(os.path.join(path,file))

#print (new_list)
    line = set()
    with open('messy_data2.txt','w') as outfile:
        for i in new_list:
            t = "Miseq_ID=" + str(i[53:87])
            #num_lines = sum(1 for lines in f)
            f = open(i, 'r')

            list1 = []
            list1.append(t)
            count = 0
            #num_lines = sum(1 for lines in f)
            #print (num_lines)
            for line in f:
                count += 1
                if line.startswith("Investigator") or line.startswith("Experiment Name") or line.startswith("Assay") or line.startswith("Description") or line.startswith("Date") :

                    line = line.replace(",", "=",1)
                    line = line.replace(",", "")
                    list1.append(line.strip())

            n = "total_samples = " + str(count - 21)
            list1.append(n)

            outfile.write("||".join(list1) + "\n")

    with open('messy_data2.txt') as infile, open(os.path.join(outputpaths,'cleaner_data2.txt'),'w') as outfile:
        whole_data = [x.strip().split("||") for x in infile]
        headers = []
        for x in whole_data:
            for k in [y.split("=")[0] for y in x]:
                if k not in headers:
                    headers.append(k)
        whole_data = [dict(y.split("=") for y in x) for x in whole_data]
        output = defaultdict(list)
        for header in headers:
            for d in whole_data:
                output[header].append(d.get(header,'NULL'))
        output = OrderedDict((x,output.get(x)) for x in headers)
        outfile.write("\t".join(list(output.keys()))+"\n")
        for row in zip(*output.values()):
            outfile.write("\t".join(row)+"\n")
    #os.system("cp "+"cleaner_data2.txt "+outputpaths)

def graph(inputpaths,outputpaths):
    a=pd.read_table(os.path.join(outputpaths,"cleaner_data2.txt"),sep="\t")
    a_filter=a.sort_values(by="total_samples ",ascending=False)
    #print(a_filter)
    plt.figure(figsize=(25,25))
    ax=sns.barplot(x="total_samples ",y="Experiment Name",data=a_filter)
    sns.set(font_scale=1)
    plt.tight_layout()
    plt.savefig(os.path.join(outputpaths,"sample_number.png"))

def select_table(outputpaths,e_name):
    a=pd.read_table(os.path.join(outputpaths,"cleaner_data2.txt"),sep="\t")
    a_filter=a.sort_values(by="total_samples ",ascending=False)
    sub_a=a[a['Experiment Name'].str.contains(e_name,na=False)]
    sub_a.to_csv(os.path.join(outputpaths,e_name+".csv"))

def select_table_person(outputpaths,i_name):
    a=pd.read_table(os.path.join(outputpaths,"cleaner_data2.txt"),sep="\t")
    a_filter=a.sort_values(by="total_samples ",ascending=False)
    sub_a=a[a['Investigator Name'].str.contains(i_name,na=False)]
    if len(sub_a) !=0:
        sub_a.to_csv(os.path.join(outputpaths,i_name+".csv"))

def setup(args):
    if args.citation:
        print(CITATION)
        sys.exit(0)
    if args.version:
        print(VERSION)
        sys.exit(0)
    if args.check_dependencies:
        for exe in ["python3", "cat"]:
            path = shutil.which(exe)
            if not path:
                print("Could not find {} in PATH".format(exe))
                exit(1)

            # See if the executable gives us versioning
            try:
                out = subprocess.check_output([exe, "--version"],
                                              stderr=subprocess.STDOUT)
                # Just look at the first line
                for line in out.splitlines():
                    print(line.decode("utf-8").rstrip())
                    break
            except subprocess.CalledProcessError as e:
                print("Could not find dependency {}: {}".format(exe, e))
                exit(1)
        sys.exit(0)

def main(arguments):
     parser = argparse.ArgumentParser(description='datatracking', epilog='_______') 
     parser.add_argument('-v','--version',default=False,action='store_true',help="Show the version and exit")
     parser.add_argument('--check-dependencies',default=False,action='store_true',help="Check dependencies")
     parser.add_argument('-c','--citation',default=False,action='store_true',help="show the citation and exit")
     parser.add_argument('-i','--inp',type=str,help="Input directory of miseqdata")
     parser.add_argument('-o','--outp',type=str,help="Output directory of miseqdata")
     parser.add_argument('-e_name','--experiment_name',type=str,help="key word to find in dataset")
     parser.add_argument('-i_name','--person_name',default=False,type=str,help="key word to find in dataset")
     args=parser.parse_args()
     setup(args)

     inputpaths=args.inp
     outputpaths=args.outp
     e_name=args.experiment_name
     i_name=args.person_name
   
     #parser.add_argument("dir", nargs='?', default="")
     logging.basicConfig(filename='myscripts.log',format='%(asctime)s %(message)s', level=logging.INFO)
     logging.info("Started")
     warnings.filterwarnings("ignore")
     append_files(inputpaths,outputpaths)
     warnings.filterwarnings("ignore")
     logging.basicConfig(format='%(asctime)s %(message)s')
     graph(inputpaths,outputpaths)
     logging.basicConfig(format='%(asctime)s %(message)s')
     select_table(outputpaths,e_name)
     logging.basicConfig(format='%(asctime)s %(message)s')
     select_table_person(outputpaths,i_name)
     logging.basicConfig(format='%(asctime)s %(message)s')

if __name__ == '__main__':
     main(sys.argv[1:])

