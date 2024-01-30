'''project vibrational modes stored in the force data of a .traj file onto the ground state relaxed structure'''
#import packages
import os 
import shutil 
from itertools import chain
from os import system
import numpy as np
from ase import io


print('start')
mod_list = [0.02,0.04,0.06,0.08,-0.08] #list of modulated structures for g-tensor calculations
my_modes = io.Trajectory('normalized_modes.traj','r') # read in the trajectory file
io.write('vasp_unmodulated.CONTCAR', my_modes[0]) #write the unmodulated structure
unmod_vasp = io.read('vasp_unmodulated.CONTCAR') #read in the relaxed VASP structure
unmod_orca = io.read('CuPc_onC_v3_wH.mol') #read in the relaxed ORCA structure
center_index = 298 #index of the central atom in the molecule
for mod in mod_list: #loop through all the modulated structures for one mode
		subdir = 'modulations_'+str(mod)+'/' # create a subdirectory for each 
		#test if the directory for the modulated structure has already been created, if not create the directory
		try:
			system('mkdir '+subdir)
		except: 
			print("directory already created")

		mode_scale = float(mod) # angstroms

		##### sort by distance atoms in the VASP structure
		from ase.geometry import find_mic
		# you can fully exclude an atom by not putting it in this list
		unfrozen_atom_indicies = list(range(len(unmod_vasp)))
		vectors, distances = find_mic(unmod_vasp.get_positions() - unmod_vasp.get_positions()[center_index], unmod_vasp.get_cell() )
		sorted_index_list_vasp = sorted(unfrozen_atom_indicies,  key=lambda index: distances[index],  reverse=False)
		#print(sorted_index_list_vasp)

		##### sort by distance atoms in the ORCA structure
		center_index = 188
		# you can fully exclude an atom by not putting it in this list
		unfrozen_atom_indicies = list(range(len(unmod_orca)))
		vectors, distances = find_mic(unmod_orca.get_positions() - unmod_orca.get_positions()[center_index], unmod_orca.get_cell() )
		sorted_index_list_orca = sorted(unfrozen_atom_indicies,  key=lambda index: distances[index],  reverse=False)
		#print(sorted_index_list_orca)

		
		for mode_index in range(len(my_modes)): # loop through all the modes in the trajectory file

			atoms = io.read('CuPc_onC.xyz')
			# Modes are stored in the force data of the trajectory file.  
			mode_vector = my_modes[mode_index].get_forces()
			# sort modes to address ordering differences between structures
			mode_vectors_orca = np.empty([259,3])
			for n,i in enumerate(sorted_index_list_orca): 
				mode_vectors_orca[i] = mode_vector[sorted_index_list_vasp[n]]

			# get mode energy
			mode_wavenumbers = my_modes[mode_index].get_potential_energy()

			#write modulated structure
			atoms.set_positions( atoms.get_positions()+ mode_scale* mode_vectors_orca )
			print(mode_index, 'wavenumbers', mode_wavenumbers.real*8065.5 ,"norm mode_vector", np.linalg.norm(mode_scale*mode_vectors_orca) )
			fname = subdir+'modulated_mode_%05d.xyz' % mode_index
			io.write(fname, atoms)

