#import packages
import os 
import shutil 
from itertools import chain
from os import system
import numpy as np
from ase import io

restart = False #Change to true if restarting a calculation
print('start')
mod_list = [0.02,0.04,0.06,0.08,-0.08] #list of modulated structures for g-tensor calculations
prefix = "CuPc" #File name prefic for all files produced by the script
calc_list = [1,2,3,4,5] #list of modes for g-tensor calculations

for calc in calc_list: #loop through all the modes in calc_list
	calc_dir= ("./"+prefix+'_'+str(calc)+'/') # name of directory for the calculations on this mode
	#test if the directory for the mode has already been created, if not create the directory
	try: 
		os.mkdir("./"+prefix+'_'+str(calc))
	except: 
		print("directory already created")

	for mod in mod_list: #loop through all the modulated structures for one mode
		mod_dir = calc_dir+str(mod)+'/' # name of directory for the calculations on this modulated structure
		#test if the directory for the modulated structure has already been created, if not create the directory
		try:
			os.mkdir(mod_dir)
		except: 
			print("Directory already created")
		geometry ='modulations_'+str(mod)+'/'+'modulated_mode_%05d.xyz' % calc  #name of staring geometry file 
		job_template = "job_b1027_temp.sh" # name of job_script template 
		job_run = mod_dir+"job_b1027_"+prefix+'_'+str(calc)+'_'+str(mod)+".sh" #name of the job script
		imp_template = "./template_elec.imp" # name of template input file
		imp_run = mod_dir +prefix+'_'+str(calc)+'_'+str(mod)+".imp" #name of job script template
		imp_out = mod_dir +prefix+'_'+str(calc)+'_'+str(mod)+".out" #name of output file for the calculation
		shutil.copy(imp_template, imp_run) #copy the input tempate to the correct location and file name
		if restart == True:
			#gbw = "./CuPc_onC_old.gbw" # name of wavefunction file if restarting a calcualtions
			#imp_gbw = mod_dir +'CuPc_onC_old.gbw' # name of new wavefunction file if restarting the calcualtions	
			#shutil.copy(gbw, imp_gbw) #rename wavefunction file if restarting the job
		#insert the geometry into the ORCA input file
		with open(geometry, "r") as f1: 
			t1 = f1.readlines() 
		with open(imp_run, "r") as f2: 
			t2 = f2.readlines() 
		t2.insert(31,t1[2:])
		t2 = list(chain.from_iterable(t2))
		with open(imp_run, "w") as f2: 
			#print(t2)
			f2.writelines(t2)

		shutil.copy(job_template, job_run) # copy and rename to job template
		# add the file name to the job template
		with open(job_run, "r") as f3:
			t3 = f3.readlines()
		t3.insert(22, "/projects/b1027/Kathleen_work/CODE/orca_4_2_1_linux_x86-64_shared_openmpi314/orca    "+ imp_run + '  >  ' + imp_out )
		t3.insert( 3, "#SBATCH --job-name=\"CuPc_HF_"+str(calc)+str(mod)+"\" ")
		t3 = list(chain.from_iterable(t3))
		with open( job_run, "w") as f3:
        		f3.writelines(t3)
		system('cd ' + mod_dir) # navigate to the job directory
		system('sbatch '+ job_run) #submit the job
		system('cd ../..') #navigate back to the starting directory

