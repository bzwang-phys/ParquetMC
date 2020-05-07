#!/usr/bin/python
import random
import os
import sys

##### Modify parameters here  ###############
# Cluster="Rutgers"
# Cluster="PBS"
Cluster = "local"
# Cluster="condor"

############################################

rootdir = os.getcwd()
inlist = open(rootdir+"/inlist", "r")
execute = "feyncalc.exe"
grid = "grid.data"

for index, eachline in enumerate(inlist):
    para = eachline.split()

    if len(para) == 0:
        print "All submitted!"
        break

    # if int(para[-2])==0:
    #     title="freq"
    # elif int(para[-2])==1:
    #     title="eqTime"
    # else:
    #     print "Not yet implemented!"
    #     break

    homedir = os.getcwd() + \
        "/Beta{0}_rs{1}_lambda{2}".format(para[1], para[2], para[3])
    if os.path.exists(homedir) != True:
        os.system("mkdir "+homedir)

    os.system("cp {0} {1}".format(execute, homedir))

    if os.path.exists(grid) == True:
        os.system("cp {0} {1}".format(grid, homedir))
    else:
        print "Run grid.py to generate grid.data first!"
        sys.exit(0)

    if Cluster != "Rutgers":
        infilepath = homedir+"/infile"
        if(os.path.exists(infilepath) != True):
            os.system("mkdir "+infilepath)
        outfilepath = homedir+"/outfile"
        if(os.path.exists(outfilepath) != True):
            os.system("mkdir "+outfilepath)
        jobfilepath = homedir+"/jobfile"
        if(os.path.exists(jobfilepath) != True):
            os.system("mkdir "+jobfilepath)
    else:
        infilepath = homedir

    for pid in range(int(para[-1])):

        ########## Generate input files ################
        infile = "_in"+str(pid)
        f = open(infilepath+"/"+infile, "w")
        item = para[0:-1]
        item.append(str(-int(random.random()*1000000)))
        item.append(str(pid))
        stri = " ".join(item)
        f.write(stri)
        f.close()

        ### terminal output goes here #############
        outfile = "_out"+str(pid)
        ### job file to submit to cluster  ########
        jobfile = "_job"+str(pid)+".sh"

        if Cluster == "local":
            os.chdir(homedir)
            os.system("./"+execute+" < "+infilepath+"/" +
                      infile+" > "+outfilepath+"/"+outfile+" &")
            os.chdir("..")

        elif Cluster == "condor":
            with open(jobfilepath+"/"+jobfile, "w") as fjob:
                fjob.write("executable = {0}\n".format(execute))
                fjob.write("input ={0}/{1}\n".format(infilepath, infile))
                fjob.write("output ={0}/{1}\n".format(outfilepath, outfile))
                fjob.write("initialdir ={0}\n".format(homedir))
                fjob.write("queue")

            os.chdir(homedir)
            os.system("condor_submit {0}/{1}".format(jobfilepath, jobfile))
            os.system("rm "+jobfilepath + "/"+jobfile)
            os.chdir("..")
        elif Cluster == "PBS":
            with open(jobfilepath+"/"+jobfile, "w") as fjob:
                fjob.write("#!/bin/sh\n"+"#PBS -N "+jobfile+"\n")
                fjob.write("#PBS -o "+homedir+"/Output\n")
                fjob.write("#PBS -e "+homedir+"/Error\n")
                fjob.write("#PBS -l walltime=2000:00:00\n")
                fjob.write("echo $PBS_JOBID >>"+homedir+"/id_job.log\n")
                fjob.write("cd "+homedir+"\n")
                fjob.write("./"+execute+" < "+infilepath+"/" +
                           infile+" > "+outfilepath+"/"+outfile)

            os.chdir(homedir)
            os.system("qsub "+jobfilepath + "/"+jobfile)
            os.system("rm "+jobfilepath + "/"+jobfile)
            os.chdir("..")
        else:
            print("{0} means no submission.".format(Cluster))
print("Jobs manage daemon is ended")
sys.exit(0)
