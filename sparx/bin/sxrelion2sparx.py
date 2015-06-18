#!/usr/bin/env python
# 
# ========================================================================================
# AURTHOR : Toshio Moriya
# DATE    : 2015/03/12
# 
# After running this script, use the following commands...
# $ sxheader.py sparx_stack.hdf --params=ctf --import=sprax_stack_params_ctf.txt
# $ sxheader.py sparx_stack.hdf --params=xform.projection --import=sparx_stack_params_proj3d.txt
# $ sxheader.py sparx_stack.hdf --params=active --one
# 
# ========================================================================================

from EMAN2 import *
from sparx import *
from sys import  *
import os
import sys
# import glob
# import shutil

from optparse import OptionParser
import global_def
from global_def import  *

def main():
	
	# Parse command argument
	arglist = []
	for arg in sys.argv:
		arglist.append( arg )

	progname = os.path.basename( arglist[0] )
	usage = progname + " input_star_file --output_dir=output_dir --star_section=star_section --create_stack"
	parser = OptionParser(usage, version=SPARXVERSION)

	parser.add_option("--output_dir",	   type="string",       default='work',     help="output directory path")
	parser.add_option("--star_section",	   type="string",       default='data_',    help="section title in the star file where data should be extracted (default: 'data_')")
	parser.add_option("--create_stack",	   action="store_true", default=True,       help="create particle stack (default: True)")
	
	(options,args) = parser.parse_args( arglist[1:] )

	# ------------------------------------------------------------------------------------
	# Check validity of input arguments and options
	# ------------------------------------------------------------------------------------
	if len(args) != 1:
		print( "ERROR!! Please provide path of input star file!" )
		print( "usage: " + usage)
		print( "Please run '" + progname + " -h' for detailed options")
		return 1

	# Rename arguments and options for readability
	file_path_relion_params  = args[0]
	dir_path_work            = options.output_dir
	str_relion_start_section = options.star_section
	is_enable_create_stack   = options.create_stack

	if (os.path.exists(file_path_relion_params) != True):
		print( "ERROR!! Input star file (%s) is not found." % file_path_relion_params)
		sys.exit(-1)

	if (os.path.exists(dir_path_work) == True):
		print( "ERROR!! Output directory (%s) already exists. Please delete it or use a different output directory" % dir_path_work)
		sys.exit(-1)
	

	# ------------------------------------------------------------------------------------
	# Constants
	# ------------------------------------------------------------------------------------
	# RELION params file related
	str_relion_item_acc_vol         = '_rlnVoltage'              
	str_relion_item_defocusU        = '_rlnDefocusU'            
	str_relion_item_defocusV        = '_rlnDefocusV'             
	str_relion_item_defocus_angle   = '_rlnDefocusAngle'         
	str_relion_item_cs              = '_rlnSphericalAberration'  
	str_relion_item_det_pix_size    = '_rlnDetectorPixelSize'    
	str_relion_item_mag             = '_rlnMagnification'       
	str_relion_item_amp_contrast    = '_rlnAmplitudeContrast'    
	str_relion_item_particle_source = '_rlnImageName'            
	str_relion_item_tx              = '_rlnOriginX'             
	str_relion_item_ty              = '_rlnOriginY'             
	str_relion_item_rot             = '_rlnAngleRot'            
	str_relion_item_tilt            = '_rlnAngleTilt'           
	str_relion_item_psi             = '_rlnAnglePsi'             
	str_relion_item_random_subset   = '_rlnRandomSubset'             

	# SPARX params file related
	if is_enable_create_stack: 
		file_name_stack_sparx             = 'sparx_stack.hdf'
	file_name_stack_sparx_params_ctf      = 'sparx_stack_params_ctf.txt'
	file_name_stack_sparx_params_proj3d   = 'sparx_stack_params_proj3d.txt'
	name_pattern_stack_sparx_params_chunk = 'sparx_stack_params_chunk*.txt'

	# ------------------------------------------------------------------------------------
	# STEP 1: Prepare input/output file paths
	# ------------------------------------------------------------------------------------
	# Get the original current path
	dir_origin = os.getcwd() # print dir_path_origin

	# Create work directory
	assert(os.path.exists(dir_path_work) == False)
	print('# Creating work dir...')
	os.mkdir(dir_path_work)
	
	# Create input and output file paths
	if is_enable_create_stack: 
		file_path_stack_sparx = dir_path_work + '/' + file_name_stack_sparx
		assert(os.path.exists(file_path_stack_sparx) == False)

	file_path_stack_sparx_params_ctf = dir_path_work + '/' + file_name_stack_sparx_params_ctf
	assert(os.path.exists(file_path_stack_sparx_params_ctf) == False)

	file_path_stack_sparx_params_proj3d = dir_path_work + '/' + file_name_stack_sparx_params_proj3d
	assert(os.path.exists(file_path_stack_sparx_params_proj3d) == False)	

	# ------------------------------------------------------------------------------------
	# STEP 2: Convert RELION parameters to SPARX format
	# ------------------------------------------------------------------------------------	
	
	# Initialize the loop variables 
	is_found_section = False
	is_found_loop = False

	col_relion_item_acc_vol         = -1
	col_relion_item_defocusU        = -1
	col_relion_item_defocusV        = -1
	col_relion_item_defocus_angle   = -1
	col_relion_item_cs              = -1
	col_relion_item_det_pix_size    = -1
	col_relion_item_mag             = -1
	col_relion_item_amp_contrast    = -1
	col_relion_item_particle_source = -1
	col_relion_item_tx              = -1
	col_relion_item_ty              = -1
	col_relion_item_rot             = -1
	col_relion_item_tilt            = -1
	col_relion_item_psi             = -1
	col_relion_item_random_subset   = -1
	
	i_col_relion_item = 0
	
	# Storages
	relion_entry_id = 0
	sprax_particle_id = 0
	if is_enable_create_stack: 
		img_particle = EMData()
	
	# Open input/output files
	assert(os.path.exists(file_path_relion_params) == True)
	file_relion_params = open(file_path_relion_params,'r')
	file_stack_sparx_params_ctf = open(file_path_stack_sparx_params_ctf,'w+')
	file_stack_sparx_params_proj3d = open(file_path_stack_sparx_params_proj3d,'w+')

	for i_line, str_line in enumerate(file_relion_params):
	
		# First, find data section in star file 
		if is_found_section == False:
			if str_line.find(str_relion_start_section) != -1:
				print '# Title: %s' % (str_line.rstrip('\n'))
				is_found_section = True
		# Then, ignore loop_ in star file 
		elif is_found_loop == False:
			assert(is_found_section == True)
			if str_line.find('loop_') != -1:
				is_found_loop = True
		# Process item list and data entries 
		else:
			assert((is_found_section == True) & (is_found_loop == True))
			tokens_line = str_line.split() # print tokens_line
			n_tokens_line = len(tokens_line)
					
			# First, check item list and find the column number of each item
			if str_line.find('_rln') != -1:
				# subtokens_line = tokens_line[1].split('#')
				i_col_relion_item += 1
				# print 'Updated Column Counts := %d ' % (i_col_relion_item)
				
				if str_line.find(str_relion_item_acc_vol) != -1:
					col_relion_item_acc_vol = int(i_col_relion_item)
					print '# acc. vol. column id       := %d ' % (col_relion_item_acc_vol)
				elif str_line.find(str_relion_item_defocusU) != -1:
					col_relion_item_defocusU = int(i_col_relion_item)
					print '# defocus U column id       := %d ' % (col_relion_item_defocusU)
				elif str_line.find(str_relion_item_defocusV) != -1:
					col_relion_item_defocusV = int(i_col_relion_item)
					print '# defocus V column id       := %d ' % (col_relion_item_defocusV)
				elif str_line.find(str_relion_item_defocus_angle) != -1:
					col_relion_item_defocus_angle = int(i_col_relion_item)
					print '# defocus angle column id   := %d ' % (col_relion_item_defocus_angle)
				elif str_line.find(str_relion_item_cs) != -1:
					col_relion_item_cs = int(i_col_relion_item)
					print '# cs column id              := %d ' % (col_relion_item_cs)
				elif str_line.find(str_relion_item_det_pix_size) != -1:
					col_relion_item_det_pix_size = int(i_col_relion_item)
					print '# det. pix. size column id  := %d ' % (col_relion_item_det_pix_size)
				elif str_line.find(str_relion_item_mag) != -1:
					col_relion_item_mag = int(i_col_relion_item)
					print '# mag. column id            := %d ' % (col_relion_item_mag)
				elif str_line.find(str_relion_item_amp_contrast) != -1:
					col_relion_item_amp_contrast = int(i_col_relion_item)
					print '# amp. contrast column id   := %d ' % (col_relion_item_amp_contrast)
				elif str_line.find(str_relion_item_particle_source) != -1:
					col_relion_item_particle_source = int(i_col_relion_item)
					print '# particle source column id := %d ' % (col_relion_item_particle_source)
				elif str_line.find(str_relion_item_tx) != -1:
					col_relion_item_tx = int(i_col_relion_item)
					print '# tx column id              := %d ' % (col_relion_item_tx)
				elif str_line.find(str_relion_item_ty) != -1:
					col_relion_item_ty = int(i_col_relion_item)
					print '# ty column id              := %d ' % (col_relion_item_ty)
				elif str_line.find(str_relion_item_rot) != -1:
					col_relion_item_rot = int(i_col_relion_item)
					print '# rot column id             := %d ' % (col_relion_item_rot)
				elif str_line.find(str_relion_item_tilt) != -1:
					col_relion_item_tilt = int(i_col_relion_item)
					print '# tilt column id            := %d ' % (col_relion_item_tilt)
				elif str_line.find(str_relion_item_psi) != -1:
					col_relion_item_psi = int(i_col_relion_item)
					print '# psi column id             := %d ' % (col_relion_item_psi)
				elif str_line.find(str_relion_item_random_subset) != -1:
					col_relion_item_random_subset = int(i_col_relion_item)
					print '# random subset column id   := %d ' % (col_relion_item_random_subset)
									
			# Then, read the data entries
			elif n_tokens_line == i_col_relion_item:
				relion_entry_id += 1 # start from 1
			
				# Parse this entry line and covert the parameters from RELION to SPARX formats
				sparx_acc_vol = float(tokens_line[col_relion_item_acc_vol - 1])

				relion_defocusU = float(tokens_line[col_relion_item_defocusU - 1])
				relion_defocusV = float(tokens_line[col_relion_item_defocusV - 1])
				relion_defocus_angle = float(tokens_line[col_relion_item_defocus_angle - 1])
				
				sparx_defocus = (relion_defocusU + relion_defocusV) / (2 * 10000)   # convert format from RELION to SPARX
				sparx_astig_amp = (relion_defocusU - relion_defocusV) / (2 * 10000) # convert format from RELION to SPARX
				sparx_astig_angle = 45.0 - relion_defocus_angle # convert format from RELION to SPARX

				sparx_cs = float(tokens_line[col_relion_item_cs - 1])

				relion_det_pix_size = float(tokens_line[col_relion_item_det_pix_size - 1])
				relion_mag = float(tokens_line[col_relion_item_mag - 1])
				sparx_apix = 10000 * relion_det_pix_size / relion_mag # convert um to A
				
				relion_amp_contrast = float(tokens_line[col_relion_item_amp_contrast - 1])
				sparx_amp_contrast = 100 * relion_amp_contrast # convert to %
				
				sparx_bfactor = 0 # RELION does not use B-Factor, so set it zero always

				relion_tx = float(tokens_line[col_relion_item_tx - 1])
				relion_ty = float(tokens_line[col_relion_item_ty - 1])
				
				relion_rot = float(tokens_line[col_relion_item_rot - 1])
				relion_tilt = float(tokens_line[col_relion_item_tilt - 1])
				relion_psi = float(tokens_line[col_relion_item_psi - 1])

				# Store CTF related paramters
				# list_sparx_params_ctf.append([sparx_defocus, sparx_cs, sparx_acc_vol, sparx_apix, sparx_bfactor, sparx_amp_contrast, sparx_astig_amp, sparx_astig_angle])
				file_stack_sparx_params_ctf.write('%12.6f %12.6f %12.6f %12.6f %12.6f %12.6f %12.6f %12.6f \n' % (sparx_defocus, sparx_cs, sparx_acc_vol, sparx_apix, sparx_bfactor, sparx_amp_contrast, sparx_astig_amp, sparx_astig_angle))

				# Store Projection related paramters
				relion_params_proj3d = Transform({'phi':relion_rot, 'theta':relion_tilt, 'omega':relion_psi, 'tx':relion_tx, 'ty':relion_ty, 'type':'mrc', 'tz':0})
				sparx_params_proj3d = relion_params_proj3d.get_params('spider')
				sparx_phi   = sparx_params_proj3d['phi']
				sparx_theta = sparx_params_proj3d['theta'] 
				sparx_psi   = sparx_params_proj3d['psi']
				sparx_s2x   = sparx_params_proj3d['tx'] 
				sparx_s2y   = sparx_params_proj3d['ty']
				
				# list_sparx_params_proj3d.append([sparx_phi, sparx_theta, sparx_psi, sparx_s2x, sparx_s2y])
				file_stack_sparx_params_proj3d.write('%12.6f %12.6f %12.6f %12.6f %12.6f \n' % (sparx_phi, sparx_theta, sparx_psi, sparx_s2x, sparx_s2y))

				# Store the entry id (particle id) in the corresponding subset
				relion_random_subset = int(tokens_line[col_relion_item_random_subset - 1])

				file_name_stack_sparx_params_chunk = name_pattern_stack_sparx_params_chunk.replace('*', "%1d" % relion_random_subset)
				file_path_stack_sparx_params_chunk = dir_path_work + '/' + file_name_stack_sparx_params_chunk
				file_stack_sparx_params_chunk = open(file_path_stack_sparx_params_chunk,'a')
				file_stack_sparx_params_chunk.write('%d \n' % (relion_entry_id))
				file_stack_sparx_params_chunk.close()
				
				if is_enable_create_stack: 
					# Now read image
					str_particle_source = tokens_line[col_relion_item_particle_source - 1]
					tokens_particle_source = str_particle_source.split('@')
					assert(len(tokens_particle_source) == 2)
				
					relion_local_particle_id = int(tokens_particle_source[0]) - 1 # Local Particle ID of RELION from 1 but SPARX from 0 
					relion_local_stack_path = tokens_particle_source[1]
					
					# assert(os.path.exists(relion_local_stack_path) == True)
					if(not os.path.exists(relion_local_stack_path) ):
						print ( "WARGING!! Image name (%s) specified in star file is not found. Skipping this image!!!" % str_particle_source)
					else:
						# Copy this particle image from local stack to new global stack
						n_img_relion_local_stack = EMUtil.get_image_count(relion_local_stack_path)
						assert(relion_local_particle_id < n_img_relion_local_stack)
						img_particle = get_im(relion_local_stack_path, relion_local_particle_id)
						img_particle.write_image(file_path_stack_sparx, sprax_particle_id)
						sprax_particle_id += 1
						
			else:
				print '# An Empty Line is detected after data entries. Breaking the loop...'
				print '# Detected Column Counts      := %d ' % (i_col_relion_item)
				print '# Detected Entry Counts       := %d ' % (relion_entry_id)				
				print '# Image counts added to stack := %d ' % (sprax_particle_id)				
				break;
	
	# Output the total number of particles
	if is_enable_create_stack: 
		n_img_stack_sparx = EMUtil.get_image_count(file_path_stack_sparx)
		print '# The total number of particles in the generated particle stack: %d' % (n_img_stack_sparx)
		assert(sprax_particle_id == n_img_stack_sparx)
	
	# Create parameter files for sparx 
	# write_text_row(list_sparx_params_ctf, file_path_stack_sparx_params_ctf)
	# write_text_row(list_sparx_params_proj3d, file_path_stack_sparx_params_proj3d)
	
	# Close input/output files
	file_relion_params.close()
	file_stack_sparx_params_ctf.close()
	file_stack_sparx_params_proj3d.close()
	
	
	# Restore the original current dir
	os.chdir(dir_origin)

	print '# DONE!'

if __name__ == "__main__":
	main()