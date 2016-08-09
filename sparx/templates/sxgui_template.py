#!/usr/bin/env python
#
# Author: Toshio Moriya, 11/11/2015 (toshio.moriya@mpi-dortmund.mpg.de)
#
# This software is issued under a joint BSD/GNU license. You may use the
# source code in this file under either license. However, note that the
# complete EMAN2 and SPARX software packages have some GPL dependencies,
# so you are responsible for compliance with the licenses of these packages
# if you opt to use BSD licensing. The warranty disclaimer below holds
# in either instance.
#
# This complete copyright notice must be included in any revised version of the
# source code. Additional authorship citations may be added, but existing
# author citations must be preserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
#

import sys
import os
from global_def import *
from PyQt4.Qt import *
from PyQt4 import QtGui
from PyQt4 import QtCore
from subprocess import *
from EMAN2 import *
from EMAN2.sparx import *
from EMAN2.EMAN2_cppwrap import *
from functools import partial # Use to connect event-source widget and event handler

# ========================================================================================
class SXcmd_token:
	def __init__(self):
		# ><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><
		# class variables
		self.key_base = ""          # key base name of command token (argument or option) in command line
		self.key_prefix = ""        # key prefix of of command token. None for argument, "--" or "-" for option
		self.label = ""             # User friendly name of argument or option
		self.help = ""              # Help info
		self.group = ""             # Tab group: main or advanced
		self.is_required = False    # Required argument or options. No default value are available 
		self.default = ""           # Default value
		self.type = ""              # Type of value
		self.is_in_io = False       # <Used only here> To check consistency between "usage in command line" and list in "== Input ==" and "== Output ==" sections
		self.widget = None          # <Used only in sxgui.py> Widget instances Associating with this command token
		# ><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><

# ========================================================================================
class SXcmd:
	def __init__(self):
		# ><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><
		# class variables
		self.name = ""               # Name of this command (i.e. name of sx*.py script but without .py extension)
		self.label = ""              # User friendly name of this command
		self.short_info = ""         # Short description of this command
		self.mpi_support = False     # Flag to indicate if this command suppors MPI version
		self.mpi_add_flag = False    # NOTE: 2015/11/12 Toshio Moriya. This can be removed when --MPI flag is removed from all sx*.py scripts 
		self.token_list = []         # list of command tokens. Need this to keep the order of command tokens
		self.token_dict = {}         # dictionary of command tokens, organised by key base name of command token. Easy to access a command token but looses their order
		# ><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><
		
# ========================================================================================
def construct_sxcmd_list():
	sxcmd_list = []
	
	# Actual sx commands are inserted into the following section by wikiparser.py.
	# @@@@@ START_INSERTION @@@@@
	# @@@@@ END_INSERTION @@@@@
	
	# Create command token dictionary for each SXcmd instance
	for sxcmd in sxcmd_list:
		for token in sxcmd.token_list:
			# Handle very special cases
			if token.type == "function":
				n_widgets = 2 # function type has two line edit boxes
				token.label = [token.label, "enter name of external file with .py extension containing user function"]
				token.help = [token.help, "(leave blank if file is not external to sparx)"]
				token.default = [token.default, "None"]
			# else: Do nothing for the other types
			
			# Register this to command token dictionary
			sxcmd.token_dict[token.key_base] = token
	
	return sxcmd_list

# ========================================================================================
# Provides all necessary functionarity
# tabs only contains gui and knows how to layout them
class SXPopup(QWidget):
	def __init__(self, sxcmd):
		QWidget.__init__(self)
		
		# ><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><
		# class variables
		self.sxcmd = sxcmd
		
		self.projct_dir = "sxgui_settings"
		self.gui_settings_file_path = "%s/gui_settings_%s.txt" % (self.projct_dir, self.sxcmd.name)
		# ><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><
		
		self.setWindowTitle(self.sxcmd.name)
		self.tab_main = SXTab(self, "Main")
		self.tab_advance = SXTab(self, "Advanced")
		self.tab_main.w1 = self.tab_advance
		self.TabWidget = QtGui.QTabWidget()
		self.TabWidget.insertTab(0, self.tab_main, self.tab_main.name)
		self.TabWidget.insertTab(1, self.tab_advance, self.tab_advance.name)
		self.TabWidget.resize(900,1080) # self.TabWidget.resize(730,860)
		self.TabWidget.show()
		
		# Load the previously saved parameter setting of this sx command
		if os.path.exists(self.gui_settings_file_path):
			self.read_params(self.gui_settings_file_path)
		
	def map_widgets_to_sxcmd_line(self):
		# Add program name to command line
		sxcmd_line = "%s.py" % self.sxcmd.name
		
		# Loop through all command tokens
		for token in self.sxcmd.token_list:
			# First, handle very special cases
			if token.type == "function":
				user_func_name_index = 0
				external_file_path_index = 1
				user_func_name = str(token.widget[user_func_name_index].text())
				external_file_path = str(token.widget[external_file_path_index].text())
				
				# This is not default value
				if external_file_path not in ["", token.default[external_file_path_index]]:
					# Case 1: User specified an exteranl function different from default or empty string
					if os.path.splitext(external_file_path)[1] != ".py": 
						QMessageBox.warning(self, "Invalid paramter value", "Exteranl File Path (%s) should include the python script extension (.py)." % (external_file_path))
						return ""
					dir_path, file_basename = os.path.split(external_file_path)
					file_basename = file_basename.replace(".py", "")
					sxcmd_line += " %s%s=[%s,%s,%s]" % (token.key_prefix, token.key_base, dir_path, file_basename, user_func_name)
				elif user_func_name != token.default[user_func_name_index]:
					# Case 2: User specified an internal function different from default
					sxcmd_line += " %s%s=%s" % (token.key_prefix, token.key_base, user_func_name)
				# else: User left default value. Do nothing
			# Then, handle the other cases
			else:
				if token.type == "bool":
					if token.is_required == True and self.key_prefix == "--": ERROR("Logical Error: Encountered unexpected condition for bool type token (%s) of command (%s). Consult with the developer." % (token.key_base, self.sxcmd.name), "%s in %s" % (__name__, os.path.basename(__file__)))
					if (token.widget.checkState() == Qt.Checked) != token.default:
						sxcmd_line += " %s%s" % (token.key_prefix, token.key_base)
				else:
					if token.is_required == True and token.widget.text() == token.default:
						QMessageBox.warning(self, "Invalid paramter value", "Token (%s) of command (%s) is required. Please set the value for this token." % (token.key_base, self.sxcmd.name))
						return ""
				
					if token.widget.text() != token.default:
						# For now, using line edit box for the other type
						widget_text = str(token.widget.text())
						if token.type not in ["int", "float"]:
							# Always enclose the string value with single quotes (')
							widget_text = widget_text.strip("\'")  # make sure the string is not enclosed by (')
							widget_text = widget_text.strip("\"")  # make sure the string is not enclosed by (")
							widget_text = "\'%s\'" % (widget_text) # then, enclose the string value with single quotes (')
						
						if token.key_prefix == "":
							sxcmd_line += " %s" % (widget_text)
						elif token.key_prefix == "--":
							sxcmd_line += " %s%s=%s" % (token.key_prefix, token.key_base, widget_text)
						else:
							ERROR("Logical Error: Encountered unexpected prefix for token (%s) of command (%s). Consult with the developer." % (token.key_base, self.sxcmd.name), "%s in %s" % (__name__, os.path.basename(__file__)))
				
		
		return sxcmd_line
	
	def generate_cmd_line(self):
		# Generate SX command line 
		sxcmd_line = self.map_widgets_to_sxcmd_line()
		
		if sxcmd_line:
			# SX command line is not empty
			# If mpi is not supported set number of MPI processer (np) to 1
			np = 1
			if self.sxcmd.mpi_support:
				# mpi is supported
				np = int(str(self.tab_main.mpi_nproc_edit.text()))
				# NOTE: 2015/10/27 Toshio Moriya
				# Since we now assume sx*.py exists in only MPI version, always add --MPI flag if necessary
				# This is not elegant but can be removed when --MPI flag is removed from all sx*.py scripts 
				if self.sxcmd.mpi_add_flag:
					sxcmd_line += " --MPI"
		
			# Generate command line according to the case
			cmd_line = ""
			if self.tab_main.qsub_enable_checkbox.checkState() == Qt.Checked:
				# Case 1: queue submission is enabled (MPI can be supported or unsupported)
				# Create script for queue submission from a give template
				if os.path.exists(self.tab_main.qsub_script_edit.text()) != True: 
					QMessageBox.warning(self, "Invalid paramter value", "Invalid file path for qsub script template (%s)." % (self.tab_main.qsub_script_edit.text()))
					return "" 
					
				file_template = open(self.tab_main.qsub_script_edit.text(),"r")
				# Extract command line from qsub script template 
				for line in file_template:
					if line.find("XXX_SXCMD_LINE_XXX") != -1:
						cmd_line = line.replace("XXX_SXCMD_LINE_XXX", sxcmd_line)
						if cmd_line.find("XXX_SXMPI_NPROC_XXX") != -1:
							cmd_line = cmd_line.replace("XXX_SXMPI_NPROC_XXX", str(np))
						if cmd_line.find("XXX_SXMPI_JOB_NAME_XXX") != -1:
							cmd_line = cmd_line.replace("XXX_SXMPI_JOB_NAME_XXX", str(self.tab_main.qsub_job_name_edit.text()))
				file_template.close()
			elif self.sxcmd.mpi_support:
				# Case 2: queue submission is disabled, but MPI is supported
				if self.tab_main.qsub_enable_checkbox.checkState() == Qt.Checked: ERROR("Logical Error: Encountered unexpected condition for tab_main.qsub_enable_checkbox.checkState. Consult with the developer.", "%s in %s" % (__name__, os.path.basename(__file__)))
				# Add MPI execution to command line
				cmd_line = str(self.tab_main.mpi_cmd_line_edit.text())
				# If empty string is entered, use a default template
				if cmd_line == "":
					cmd_line = "mpirun -np XXX_SXMPI_NPROC_XXX XXX_SXCMD_LINE_XXX"
				if cmd_line.find("XXX_SXMPI_NPROC_XXX") != -1:
					cmd_line = cmd_line.replace("XXX_SXMPI_NPROC_XXX", str(np))
				if cmd_line.find("XXX_SXCMD_LINE_XXX") != -1:
					cmd_line = cmd_line.replace("XXX_SXCMD_LINE_XXX", sxcmd_line)
			else: 
				# Case 3: queue submission is disabled, and MPI is not supported
				if self.tab_main.qsub_enable_checkbox.checkState() == Qt.Checked: ERROR("Logical Error: Encountered unexpected condition for tab_main.qsub_enable_checkbox.checkState. Consult with the developer.", "%s in %s" % (__name__, os.path.basename(__file__)))
				# Use sx command as it is
				cmd_line = sxcmd_line
		else:
			# SX command line is be empty because an error happens in map_widgets_to_sxcmd_line
			cmd_line = ""
		
		return cmd_line
	
	def execute_cmd_line(self):
		# Generate command line 
		cmd_line = self.generate_cmd_line()
		
		if cmd_line:
			# Command line is not empty
			# First, check existence of outputs
			for token in self.sxcmd.token_list:
				if token.type == "output":
					if os.path.exists(token.widget.text()):
						# NOTE: 2015/11/24 Toshio Moriya
						# This special case needs to be handled with more general method...
						if self.sxcmd.name in ["sxisac", "sxviper", "sxrviper", "sxmeridien", "sxsort3d"]:
							reply = QtGui.QMessageBox.question(self, "Output Directory/File", "Output Directory/File (%s) already exists. Do you really want to run the program with continue mode?" % (token.widget.text()), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
							if reply == QtGui.QMessageBox.No:
								return
							# else: # Do nothing
						else:
							QMessageBox.warning(self, "Output Directory/File", "Output Directory/File (%s) already exists. Please change the name and try it again. Aborting execution ..." % (token.widget.text()))
							return
			
			# If mpi is not supported set number of MPI processer (np) to 1
			np = 1
			if self.sxcmd.mpi_support:
				np = int(str(self.tab_main.mpi_nproc_edit.text()))
		
			if self.tab_main.qsub_enable_checkbox.checkState() == Qt.Checked:
				# Case 1: queue submission is enabled (MPI can be supported or unsupported)
				# Create script for queue submission from a give template
				template_file_path = self.tab_main.qsub_script_edit.text()
				if os.path.exists(template_file_path) == False: 
					QMessageBox.warning(self, "Invalid paramter value", "Invalid file path for qsub script template (%s). Aborting execution ..." % (template_file_path))
					return
				file_template = open(self.tab_main.qsub_script_edit.text(),"r")
				file_name_qsub_script = "qsub_" + str(self.tab_main.qsub_job_name_edit.text()) + ".sh"
				file_qsub_script = open(file_name_qsub_script,"w")
				for line_io in file_template:
					if line_io.find("XXX_SXCMD_LINE_XXX") != -1:
						line_io = cmd_line
					else:
						if line_io.find("XXX_SXMPI_NPROC_XXX") != -1:
							line_io = line_io.replace("XXX_SXMPI_NPROC_XXX", str(np))
						if line_io.find("XXX_SXMPI_JOB_NAME_XXX") != -1:
							line_io = line_io.replace("XXX_SXMPI_JOB_NAME_XXX", str(self.tab_main.qsub_job_name_edit.text()))
					file_qsub_script.write(line_io)
				file_template.close()
				file_qsub_script.close()
				# Generate command line for queue submission
				cmd_line_in_script = cmd_line
				cmd_line = str(self.tab_main.qsub_cmd_edit.text()) + " " + file_name_qsub_script
				print "Wrote the following command line in the queue submission script: "
				print cmd_line_in_script
				print "Submitted a job by the following command: "
				print cmd_line
			else:
				# Case 2: queue submission is disabled (MPI can be supported or unsupported)
				if self.tab_main.qsub_enable_checkbox.checkState() == Qt.Checked: ERROR("Logical Error: Encountered unexpected condition for tab_main.qsub_enable_checkbox.checkState. Consult with the developer.", "%s in %s" % (__name__, os.path.basename(__file__)))
				print "Executed the following command: "
				print cmd_line
		
			# Execute the generated command line
			process = subprocess.Popen(cmd_line, shell=True)
			self.emit(QtCore.SIGNAL("process_started"), process.pid)
			
			# Save the current state of GUI settings
			if os.path.exists(self.projct_dir) == False:
				os.mkdir(self.projct_dir)
			self.write_params(self.gui_settings_file_path)
		# else: SX command line is be empty because an error happens in generate_cmd_line. Let's do nothing
	
	def save_cmd_line(self):
		# Generate command line 
		cmd_line = self.generate_cmd_line()
		if cmd_line:
			file_name_out = QtGui.QFileDialog.getSaveFileName(self, "Generate Command Line", options = QtGui.QFileDialog.DontUseNativeDialog)
			if file_name_out != "":
				file_out = open(file_name_out,"w")
				file_out.write(cmd_line + "\n")
				file_out.close()
				print "Saved the following command to %s:" % file_name_out
				print cmd_line
				
				# Save the current state of GUI settings
				if os.path.exists(self.projct_dir) == False:
					os.mkdir(self.projct_dir)
				self.write_params(self.gui_settings_file_path)
		# else: Do nothing
	
	def write_params(self, file_name_out):
		file_out = open(file_name_out,"w")
		
		# Write script name for consistency check upon loading
		file_out.write("@@@@@ %s gui setting - " % (self.sxcmd.name))
		file_out.write(EMANVERSION + " (CVS" + CVSDATESTAMP[6:-2] +")")
		file_out.write(" @@@@@ \n")
		
		# Define list of (tab) groups
		group_main = "main"
		group_advanced = "advanced"
		
		# Loop through all groups. First write out values of widgets in main tab, then ones in advanced
		for group in [group_main, group_advanced]:
			# Loop through all command tokens
			for cmd_token in self.sxcmd.token_list:
				if cmd_token.group == group:
					# First, handle very special cases
					if cmd_token.type == "function":
						# This type has two line edit boxes as a list of widget
						n_widgets = 2
						for widget_index in xrange(n_widgets):
							val_str = str(cmd_token.widget[widget_index].text()) 
							file_out.write("<%s> %s (default %s) == %s \n" % (cmd_token.key_base, cmd_token.label[widget_index], cmd_token.default[widget_index], val_str))
					# Then, handle the other cases
					else:
						val_str = ""
						if cmd_token.type == "bool":
							if cmd_token.widget.checkState() == Qt.Checked:
								val_str = "YES"
							else:
								val_str = "NO"
						else:
							# The other type has only one line edit box
							val_str = str(cmd_token.widget.text())
						
						if cmd_token.is_required == False:
							file_out.write("<%s> %s (default %s) == %s \n" % (cmd_token.key_base, cmd_token.label, cmd_token.default, val_str))
						else:
							file_out.write("<%s> %s (default required %s) == %s \n" % (cmd_token.key_base, cmd_token.label, cmd_token.type, val_str))
				# else: do nothig
			
		# At the end of parameter file...
		# Write MPI parameters 
		file_out.write("%s == %s \n" % ("MPI processors", str(self.tab_main.mpi_nproc_edit.text())))
		file_out.write("%s == %s \n" % ("MPI Command Line Template", str(self.tab_main.mpi_cmd_line_edit.text())))
		# Write Qsub paramters 
		if self.tab_main.qsub_enable_checkbox.checkState() == Qt.Checked:
			val_str = "YES"
		else:
			val_str = "NO"
		file_out.write("%s == %s \n" % ("Submit Job to Queue", val_str))	
		file_out.write("%s == %s \n" % ("Job Name", str(self.tab_main.qsub_job_name_edit.text())))
		file_out.write("%s == %s \n" % ("Submission Command", str(self.tab_main.qsub_cmd_edit.text())))
		file_out.write("%s == %s \n" % ("Submission Script Template", str(self.tab_main.qsub_script_edit.text())))
		
		file_out.close()
			
	def read_params(self, file_name_in):
		file_in = open(file_name_in,"r")
	
		# Check if this parameter file is for this sx script
		line_in = file_in.readline()
		if line_in.find("@@@@@ %s gui setting" % (self.sxcmd.name)) != -1:
			n_function_type_lines = 2
			function_type_line_counter = 0
			# loop through the rest of lines
			for line_in in file_in:
				# Extract label (which should be left of "=="). Also strip the ending spaces
				label_in = line_in.split("==")[0].strip()
				# Extract value (which should be right of "=="). Also strip all spaces
				val_str_in = line_in.split("==")[1].strip() 
				
				if label_in == "MPI processors":
					self.tab_main.mpi_nproc_edit.setText(val_str_in)
				elif label_in == "MPI Command Line Template":
					self.tab_main.mpi_cmd_line_edit.setText(val_str_in)
				elif label_in == "Submit Job to Queue":
					if val_str_in == "YES":
						self.tab_main.qsub_enable_checkbox.setChecked(True)
					else:
						assert val_str_in == "NO"
						self.tab_main.qsub_enable_checkbox.setChecked(False)
				elif label_in == "Job Name":
					self.tab_main.qsub_job_name_edit.setText(val_str_in)
				elif label_in == "Submission Command":
					self.tab_main.qsub_cmd_edit.setText(val_str_in)
				elif label_in == "Submission Script Template":
					self.tab_main.qsub_script_edit.setText(val_str_in)
				else:
					# Extract key_base of this command token
					target_operator = "<"
					item_tail = label_in.find(target_operator)
					if item_tail != 0: 
						QMessageBox.warning(self, "Invalid Paramter File Format", "Command token entry should start from \"%s\" for key base name in line (%s). The format of this file might be corrupted. Please save the paramater file again." % (target_operator, line_in))
					label_in = label_in[item_tail + len(target_operator):].strip() # Get the rest of line
					target_operator = ">"
					item_tail = label_in.find(target_operator)
					if item_tail == -1: 
						QMessageBox.warning(self, "Invalid Paramter File Format", "Command token entry should have \"%s\" closing key base name in line (%s) The format of this file might be corrupted. Please save the paramater file again." % (target_operator, line_in))
					key_base = label_in[0:item_tail]
					# Get corresponding cmd_token
					if key_base not in self.sxcmd.token_dict.keys(): 
						QMessageBox.warning(self, "Invalid Paramter File Format", "Invalid base name of command token \"%s\" is found in line (%s). This paramter file might be imcompatible with the current version. Please save the paramater file again." % (key_base, line_in))
					cmd_token = self.sxcmd.token_dict[key_base]
					# First, handle very special cases
					if cmd_token.type == "function":
						cmd_token.widget[function_type_line_counter].setText(val_str_in)
						function_type_line_counter += 1
						function_type_line_counter %= n_function_type_lines # function have two line edit boxes
					# Then, handle the other cases
					else:
						if cmd_token.type == "bool":
							# construct new widget(s) for this command token
							if val_str_in == "YES":
								cmd_token.widget.setChecked(True)
							else: # val_str_in == "NO"
								cmd_token.widget.setChecked(False)
						else:
							# For now, use line edit box for the other type
							cmd_token.widget.setText(val_str_in)
						
		else:
			QMessageBox.warning(self, "Fail to load paramters", "The specified file is not paramter file for %s." % self.sxcmd.name)
		
		file_in.close()
	
	def save_params(self):
		file_path = str(QtGui.QFileDialog.getSaveFileName(self, "Save Parameters", options = QtGui.QFileDialog.DontUseNativeDialog))
		if file_path != "":
			self.write_params(file_path)
	
	def load_params(self):
		file_path = str(QtGui.QFileDialog.getOpenFileName(self, "Load parameters", options = QtGui.QFileDialog.DontUseNativeDialog))
		if file_path != "":
			self.read_params(file_path)
	
	def select_file(self, target_edit_box, file_format = ""):
		file_path = ""
		if file_format == "bdb":
			file_path = str(QtGui.QFileDialog.getOpenFileName(self, "Select BDB File", "", "BDB files (*.bdb)", options = QtGui.QFileDialog.DontUseNativeDialog))
			# Use relative path. 
			if file_path:
				file_path = "bdb:./" + os.path.relpath(file_path).replace("EMAN2DB/", "#").replace(".bdb", "")
				file_path = file_path.replace("/#", "#")
		elif file_format == "py":
			file_path = str(QtGui.QFileDialog.getOpenFileName(self, "Select Python File", "", "PY files (*.py)", options = QtGui.QFileDialog.DontUseNativeDialog))
			# Use full path
		elif file_format == "pdb":
			file_path = str(QtGui.QFileDialog.getOpenFileName(self, "Select PDB File", "", "PDB files (*.pdb *.pdb1)", options = QtGui.QFileDialog.DontUseNativeDialog))
			# Use relative path. 
			if file_path:
				file_path = os.path.relpath(file_path)
		else:
			if file_format:
				file_path = str(QtGui.QFileDialog.getOpenFileName(self, "Select %s File" % (file_format.upper()), "", "%s files (*.%s)"  % (file_format.upper(), file_format), options = QtGui.QFileDialog.DontUseNativeDialog))
			else:
				file_path = str(QtGui.QFileDialog.getOpenFileName(self, "Select File", "", "All files (*.*)", options = QtGui.QFileDialog.DontUseNativeDialog))
			# Use relative path. 
			if file_path:
				file_path = os.path.relpath(file_path)
			
		if file_path != "":
			target_edit_box.setText(file_path)
				
	def select_dir(self, target_edit_box):
		dir_path = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory", "", options = QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.DontUseNativeDialog))
		if dir_path != "":
			# Use relative path. 
			target_edit_box.setText(os.path.relpath(dir_path))
			
	"""
#	def show_output_info(self):
#		QMessageBox.information(self, "sx* output","outdir is the name of the output folder specified by the user. If it does not exist, the directory will be created. If it does exist, the program will crash and an error message will come up. Please change the name of directory and restart the program.")
	"""

# ========================================================================================
class SXTab(QWidget):

	def __init__(self, parent, name):
		QWidget.__init__(self, parent)
		
		# ><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><
		# class variables
		self.name = name
		self.sxpopup = parent
		
		# layout parameters
		self.y1 = 10
		# self.y2 = self.y1 + 95 #self.y2 = self.y1 + 98
		
		self.x1 = 10
		self.x2 = self.x1 + 500 # self.x2 = self.x1 + 200
		self.x3 = self.x2 + 135
		self.x4 = self.x3 + 100
		self.x5 = 230
		# ><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><
		tab_group = self.name.lower()
		
		if tab_group == "main":
			# # Set the window title
			# self.setWindowTitle(self.sxcmd.name)
			# Set a label and its position in this tab
			temp_label = QtGui.QLabel("<b>%s</b>" % (self.sxpopup.sxcmd.name), self)
			temp_label.move(self.x1, self.y1)
			# NOTE: 2015/11/17 Toshio Moriya
			# Necessary to separate "<b>%s</b>" from the information for avoiding to invoke the tag interpretations of string
			# e.g. < becomes the escape character
			temp_label = QtGui.QLabel("%s" % (self.sxpopup.sxcmd.short_info), self)
			temp_label.setWordWrap(True)
			temp_label.setFixedWidth(600)
			temp_label.move(self.x1 + 100, self.y1)
			self.y1 += 50
			
			# Add load paramater button 
			self.load_params_btn = QPushButton("Load parameters", self)
			self.load_params_btn.move(self.x1 - 5, self.y1)
			self.load_params_btn.setToolTip("Load gui parameter settings to retrieve a previously-saved one")
			self.connect(self.load_params_btn, SIGNAL("clicked()"), self.sxpopup.load_params)
			self.y1 += 25
			
		elif tab_group == "advanced":
		# Set the window title
			#self.setWindowTitle("%s advanced parameter selection" % self.sxcmd.name)
			# Set a label and its position in this tab
			temp_label = QtGui.QLabel("<b>%s</b>" % (self.sxpopup.sxcmd.name), self)
			temp_label.move(self.x1, self.y1)
			temp_label = QtGui.QLabel("Set advanced parameters", self)
			temp_label.setWordWrap(True)
			temp_label.setFixedWidth(600)
			temp_label.move(self.x1 + 100, self.y1)
			self.y1 += 25
		
		# Add space
		self.y1 = self.y1 + 25 * 1
		
		# Add widget for editing command args and options
		for cmd_token in self.sxpopup.sxcmd.token_list:
			if cmd_token.group == tab_group:
				
				# First, handle very special cases
				if cmd_token.type == "function":
					n_widgets = 2 # function type has two line edit boxes
					cmd_token_widget = [None] * n_widgets
					
					# Create widgets for user function name
					widget_index = 0
					label_widget = QtGui.QLabel(cmd_token.label[widget_index], self)
					label_widget.move(self.x1, self.y1)
					cmd_token_widget[widget_index] = QtGui.QLineEdit(self)
					cmd_token_widget[widget_index].setText(cmd_token.default[widget_index])
					cmd_token_widget[widget_index].move(self.x2,self.y1 - 7)
					cmd_token_widget[widget_index].setToolTip(cmd_token.help[widget_index])
					
					self.y1 = self.y1 + 25
					
					# Create widgets for external file path containing above user function
					widget_index = 1
					label_widget = QtGui.QLabel(cmd_token.label[widget_index], self)
					label_widget.move(self.x1, self.y1)
					label_widget = QtGui.QLabel(cmd_token.help[widget_index], self)
					label_widget.move(self.x1, self.y1 + 25)
					cmd_token_widget[widget_index] = QtGui.QLineEdit(self)
					cmd_token_widget[widget_index].setText(cmd_token.default[widget_index]) # Because default user functions is internal
					cmd_token_widget[widget_index].move(self.x2,self.y1 - 7)
					cmd_token_widget[widget_index].setToolTip(cmd_token.help[widget_index])
					file_format = "py"
					temp_btn = QPushButton("Select External File", self)
					temp_btn.move(self.x3, self.y1 - 10)
					self.connect(temp_btn, QtCore.SIGNAL("clicked()"), partial(self.sxpopup.select_file, cmd_token_widget[widget_index], file_format))
					
					self.y1 = self.y1 + 25 * 2
				# Then, handle the other cases
				else:
					# Create label widget 
					label_widget = QtGui.QLabel(cmd_token.label, self)
					label_widget.move(self.x1, self.y1)
					
					# Create widget and associate it to this cmd_token
					cmd_token_widget = None
					if cmd_token.type == "bool":
						# construct new widget(s) for this command token
						cmd_token_widget = QtGui.QCheckBox("", self)
						cmd_token_widget.setCheckState(cmd_token.default)
					else:
						if cmd_token.type == "image":
							cmd_token_widget = QtGui.QLineEdit(self)
							cmd_token_widget.setText(cmd_token.default)
							file_format = "hdf"
							temp_btn = QPushButton("Select .%s" % file_format, self)
							temp_btn.move(self.x3, self.y1 - 12)
							self.connect(temp_btn, QtCore.SIGNAL("clicked()"), partial(self.sxpopup.select_file, cmd_token_widget, file_format))
							file_format = "bdb"
							temp_btn = QPushButton("Select .%s" % file_format, self)
							temp_btn.move(self.x4, self.y1 - 12)
							self.connect(temp_btn, QtCore.SIGNAL("clicked()"), partial(self.sxpopup.select_file, cmd_token_widget, file_format))
						elif cmd_token.type == "any_image":
							cmd_token_widget = QtGui.QLineEdit(self)
							cmd_token_widget.setText(cmd_token.default)
							temp_btn = QPushButton("Select Image File", self)
							temp_btn.move(self.x3, self.y1 - 12)
							self.connect(temp_btn, QtCore.SIGNAL("clicked()"), partial(self.sxpopup.select_file, cmd_token_widget))
							file_format = "bdb"
							temp_btn = QPushButton("Select .%s" % file_format, self)
							temp_btn.move(self.x4 + 40, self.y1 - 12)
							self.connect(temp_btn, QtCore.SIGNAL("clicked()"), partial(self.sxpopup.select_file, cmd_token_widget, file_format))
						elif cmd_token.type == "pdb":
							cmd_token_widget = QtGui.QLineEdit(self)
							cmd_token_widget.setText(cmd_token.default)
							file_format = "pdb"
							temp_btn = QPushButton("Select .%s" % file_format, self)
							temp_btn.move(self.x3, self.y1 - 12)
							self.connect(temp_btn, QtCore.SIGNAL("clicked()"), partial(self.sxpopup.select_file, cmd_token_widget, file_format))
						elif cmd_token.type == "parameters":
							cmd_token_widget = QtGui.QLineEdit(self)
							cmd_token_widget.setText(cmd_token.default)
							temp_btn = QPushButton("Select Paramter File", self)
							temp_btn.move(self.x3, self.y1 - 12)
							self.connect(temp_btn, QtCore.SIGNAL("clicked()"), partial(self.sxpopup.select_file, cmd_token_widget))
						elif cmd_token.type == "directory":
							cmd_token_widget = QtGui.QLineEdit(self)
							cmd_token_widget.setText(cmd_token.default)
							temp_btn = QPushButton("Select directory", self)
							temp_btn.move(self.x3, self.y1 - 12)
							self.connect(temp_btn, QtCore.SIGNAL("clicked()"), partial(self.sxpopup.select_dir, cmd_token_widget))
						elif cmd_token.type == "output":
							cmd_token_widget = QtGui.QLineEdit(self)
							cmd_token_widget.setText(cmd_token.default)
						else:
							if cmd_token.type not in ["int", "float", "string"]: ERROR("Logical Error: Encountered unsupported type (%s). Consult with the developer."  % cmd_token.type, "%s in %s" % (__name__, os.path.basename(__file__)))
							cmd_token_widget = QtGui.QLineEdit(self)
							cmd_token_widget.setText(cmd_token.default)
						
					cmd_token_widget.move(self.x2,self.y1 - 7)
					cmd_token_widget.setToolTip(cmd_token.help)
				
					self.y1 = self.y1 + 25
				
				# Register this widget
				cmd_token.widget = cmd_token_widget
				
		if tab_group == "main":
			# Add space
			self.y1 = self.y1 + 25 * 1
		
			# Add gui components for MPI related paramaters if necessary
			temp_label = QtGui.QLabel("MPI processors", self)
			temp_label.move(self.x1, self.y1)
			self.mpi_nproc_edit = QtGui.QLineEdit(self)
			self.mpi_nproc_edit.setText("1")
			self.mpi_nproc_edit.move(self.x2, self.y1)
			self.mpi_nproc_edit.setToolTip("The number of processors to use. Default is single processor mode")
		
			self.y1 = self.y1 + 25

			temp_label = QtGui.QLabel("MPI command line template", self)
			temp_label.move(self.x1, self.y1)
			self.mpi_cmd_line_edit = QtGui.QLineEdit(self)
			self.mpi_cmd_line_edit.setText("")
			self.mpi_cmd_line_edit.move(self.x2, self.y1)
			self.mpi_cmd_line_edit.setToolTip("The template of MPI command line (e.g. \"mpirun -np XXX_SXMPI_NPROC_XXX --host n0,n1,n2 XXX_SXCMD_LINE_XXX\"). If empty, use \"mpirun -np XXX_SXMPI_NPROC_XXX XXX_SXCMD_LINE_XXX\"")

			self.y1 = self.y1 + 25
		
			# If MPI is not supported, disable this widget
			self.set_widget_enable_state(self.mpi_nproc_edit, self.sxpopup.sxcmd.mpi_support)
			self.set_widget_enable_state(self.mpi_cmd_line_edit, self.sxpopup.sxcmd.mpi_support)

			# Add gui components for queue submission (qsub)
			is_qsub_enabled = False
			temp_label = QtGui.QLabel("submit job to queue", self)
			temp_label.move(self.x1, self.y1)
			self.qsub_enable_checkbox = QtGui.QCheckBox("", self)
			self.qsub_enable_checkbox.setCheckState(is_qsub_enabled)
			self.qsub_enable_checkbox.stateChanged.connect(self.set_qsub_enable_state) # To control enable state of the following qsub related widgets
			self.qsub_enable_checkbox.move(self.x2, self.y1)
			self.qsub_enable_checkbox.setToolTip("submit job to queue")
		
			self.y1 = self.y1 + 25
		
			temp_label = QtGui.QLabel("job name", self)
			temp_label.move(self.x1, self.y1)
			self.qsub_job_name_edit = QtGui.QLineEdit(self)
			self.qsub_job_name_edit.setText(self.sxpopup.sxcmd.name)
			self.qsub_job_name_edit.move(self.x2, self.y1)
			self.qsub_job_name_edit.setToolTip("name of this job")

			self.y1 = self.y1 + 25

			temp_label = QtGui.QLabel("submission command", self)
			temp_label.move(self.x1, self.y1)
			self.qsub_cmd_edit = QtGui.QLineEdit(self)
			self.qsub_cmd_edit.setText("qsub")
			self.qsub_cmd_edit.move(self.x2, self.y1)
			self.qsub_cmd_edit.setToolTip("name of submission command to queue job")

			self.y1 = self.y1 + 25

			temp_label = QtGui.QLabel("submission script template", self)
			temp_label.move(self.x1, self.y1)
			self.qsub_script_edit = QtGui.QLineEdit(self)
			self.qsub_script_edit.setText("msgui_qsub.sh")
			self.qsub_script_edit.move(self.x2, self.y1)
			self.qsub_script_edit.setToolTip("file name of submission script template (e.g. $EMAN2DIR/bin/msgui_qsub.sh)")
			self.qsub_script_open_btn = QPushButton("Select Template File", self)
			self.qsub_script_open_btn.move(self.x3, self.y1 - 4)
			self.connect(self.qsub_script_open_btn, QtCore.SIGNAL("clicked()"), partial(self.sxpopup.select_file, self.qsub_script_edit))

			self.y1 = self.y1 + 25
		
			# Initialize enable state of qsub related widgets
			self.set_qsub_enable_state()
		
			# Add space
			self.y1 = self.y1 + 25 * 1

			# Add save paramater button 
			self.save_params_btn = QPushButton("Save parameters", self)
			self.save_params_btn.move(self.x1-5, self.y1)
			self.save_params_btn.setToolTip("Save gui parameter settings")
			self.connect(self.save_params_btn, SIGNAL("clicked()"), self.sxpopup.save_params)
		
			self.y1 = self.y1 + 30

			self.cmd_line_btn = QPushButton("Generate command line", self)
			self.cmd_line_btn.move(self.x1-5, self.y1)
			self.cmd_line_btn.setToolTip("Generate command line from gui parameter settings")
			self.connect(self.cmd_line_btn, SIGNAL("clicked()"), self.sxpopup.save_cmd_line)
		
			self.y1 = self.y1 + 30

			# Add a run button
			self.execute_btn = QtGui.QPushButton("Run %s" % self.sxpopup.sxcmd.name, self)
			# make 3D textured push button look
			s = "QPushButton {font: bold; color: #000;border: 1px solid #333;border-radius: 11px;padding: 2px;background: qradialgradient(cx: 0, cy: 0,fx: 0.5, fy:0.5,radius: 1, stop: 0 #fff, stop: 1 #8D0);min-width:90px;margin:5px} QPushButton:pressed {font: bold; color: #000;border: 1px solid #333;border-radius: 11px;padding: 2px;background: qradialgradient(cx: 0, cy: 0,fx: 0.5, fy:0.5,radius: 1, stop: 0 #fff, stop: 1 #084);min-width:90px;margin:5px}"
			self.execute_btn.setStyleSheet(s)
			self.execute_btn.move(self.x5, self.y1)
			self.connect(self.execute_btn, SIGNAL("clicked()"), self.sxpopup.execute_cmd_line)

	def set_widget_enable_state(self, widget, is_enabled):
		# Set enable state and background color of widget according to enable state
		bg_color = Qt.white
		if is_enabled == False:
			bg_color = Qt.gray
		
		widget.setEnabled(is_enabled)
		widget_palette = widget.palette()
		widget_palette.setColor(widget.backgroundRole(), bg_color)
		widget.setPalette(widget_palette)

	def set_qsub_enable_state(self):
		is_enabled = False
		if self.qsub_enable_checkbox.checkState() == Qt.Checked:
			is_enabled = True
		
		# Set enable state and background color of mpi related widgets
		if self.sxpopup.sxcmd.mpi_support:
			self.set_widget_enable_state(self.mpi_cmd_line_edit, not is_enabled)
		
		# Set enable state and background color of qsub related widgets
		self.set_widget_enable_state(self.qsub_job_name_edit, is_enabled)
		self.set_widget_enable_state(self.qsub_cmd_edit, is_enabled)
		self.set_widget_enable_state(self.qsub_script_edit, is_enabled)
		self.set_widget_enable_state(self.qsub_script_open_btn, is_enabled)

# ========================================================================================
# Layout of the Pop Up window SXPopup_info; started by the function info of the main window
class SXPopup_info(QWidget):
	def __init__(self):
		QWidget.__init__(self)
		#Here we just set the window title and  3 different labels, with their positions in the window
		self.setWindowTitle("Sparx GUI Info Page")
		title1=QtGui.QLabel("<b>Sparx GUI Prototype</b>", self)
		title1.move(10,10)
		title2=QtGui.QLabel("<b>Authors: Toshio Moriya</b> ", self)
		title2.move(10,40)
		title3=QtGui.QLabel("For more information visit:\n%s " % SPARX_DOCUMENTATION_WEBSITE, self)
		title3.move(10,70)

# ========================================================================================
# Main Window (started by class App)
# This class includes the layout of the main window
class MainWindow(QtGui.QWidget):
	def __init__(self):
		QtGui.QWidget.__init__(self)
		
		# self.setStyleSheet("background-image: url("1.png")")
		# Set the title of the window
		self.setWindowTitle("MPI-SPARX GUI (Alpha Version)")
		self.setAutoFillBackground(True)
		palette = QPalette(self)
		palette.setBrush(QPalette.Background, QBrush(QPixmap(get_image_directory() + "sxgui.py_main_window_background_image.png")))
		# palette.setBrush(QPalette.Background, QBrush(QPixmap("Fig6.png")))
		# palette.setBrush(QPalette.Background, QBrush(QPixmap("spaxgui02.png")))
		self.setPalette(palette)
		
		# --------------------------------------------------------------------------------
		# General 
		# --------------------------------------------------------------------------------
		# Add title label and set position and font style
		title=QtGui.QLabel("<span style=\'font-size:18pt; font-weight:600; color:#aa0000;\'><b>PROGRAMS </b></span><span style=\'font-size:12pt; font-weight:60; color:#aa0000;\'>(shift-click for wiki)</span>", self)
		title.move(17,47)
		QtGui.QToolTip.setFont(QtGui.QFont("OldEnglish", 8))

		# Add Push button to display popup window for info about the application
		self.btn_info = QPushButton(self)
		self.connect(self.btn_info, SIGNAL("clicked()"), self.info)
		icon = QIcon(get_image_directory() + "sparxicon.png") # Decorates the button with the sparx image
		self.btn_info.setIcon(icon)
		self.btn_info.move(5, 5)
		self.btn_info.setToolTip("Info Page")

		# Add Close button
		self.btn_quit = QPushButton("Close", self)
		self.btn_quit.setToolTip("Close SPARX GUI ")
		self.btn_quit.move(65, 5)
		self.connect(self.btn_quit, QtCore.SIGNAL("clicked()"),QtGui.qApp, QtCore.SLOT("quit()"))
		
		# --------------------------------------------------------------------------------
		# SX Commands (sx*.py)
		# --------------------------------------------------------------------------------
		self.y1 = 95
		
		# Construct list of sxscript objects (extracted from associated wiki documents)
		sxcmd_list = construct_sxcmd_list()
		
		for sxcmd in sxcmd_list:
			# Add buttons for this sx*.py processe
			temp_btn = QPushButton(sxcmd.label, self)
			temp_btn.move(10, self.y1)
			temp_btn.setToolTip(sxcmd.short_info)
			self.connect(temp_btn, SIGNAL("clicked()"), partial(self.handle_sxcmd_btn_event, sxcmd))

			self.y1 += 30
			
		# Set the width and height of the main window
		self.resize(300,400)

	# Click actions: The following functions are associated with the click event of push buttons (btn##) on the main window. 
	def handle_sxcmd_btn_event(self, sxcmd):
		modifiers = QtGui.QApplication.keyboardModifiers()
		if modifiers == QtCore.Qt.ShiftModifier:
			os.system("python -m webbrowser %s%s" % (SPARX_DOCUMENTATION_WEBSITE, sxcmd.name))
			return
			
		self.w = SXPopup(sxcmd)
		
	#This is the function info, which is being started when the Pushbutton btn_info of the main window is being clicked
	def info(self):
		# print "Opening a new popup window..."
		# Opens the window SXPopup_info, and defines its width and height
		# The layout of the SXPopup_info window is defined in class SXPopup_info(QWidget Window)
		self.w = SXPopup_info()
		self.w.resize(250,200)
		self.w.show()

# ========================================================================================
#  This is the main class of the program
#  Here we provide the necessary imports. The basic GUI widgets are located in QtGui module.
class App(QApplication):
	def __init__(self, *args):
		QApplication.__init__(self, *args)
		# Define the main window (class MainWindow)
		self.main = MainWindow()
		# self.main.resize(400,450)
		self.main.resize(1000, 755)
		# Define that when all windows are closed, function byebye of class App will be started
		self.connect(self, SIGNAL("lastWindowClosed()"), self.byebye )
		# Show main window
		self.main.show()
		
	#function byebye (just quit)  
	def byebye( self ):
		print" bye bye!"
		self.exit(0)

# ========================================================================================
#  Necessary for execution of the program
def main(args):
	from optparse import OptionParser
	progname = os.path.basename(sys.argv[0])
	usage = """%prog [options] <image>
		
Automatic and manual particle selection. This version is specifically aimed at square boxes
for single particle analysis."""
	parser = OptionParser(usage=usage,version=EMANVERSION)

	parser.add_option("--demo", type="string", default="",   help="Name of the demo whose input parameters should be used to initialize the GUI fields: --demo=mpibdb means the input parameters in demo/mpi_bdb will be used, --demo=mpibdbctf means the input parameters in demo/mpi_bdb_ctf will be used")
	global options
	(options, args) = parser.parse_args()
	global DEMO_mpibdbctf
	DEMO_mpibdbctf = "mpibdbctf"
	global DEMO_mpibdb
	DEMO_mpibdb = "mpibdb"
	
	global app
	app = App(args)
	app.setWindowIcon(QIcon(get_image_directory()+"sparxicon.png"))
	
	app.main.show()
	app.main.raise_()
	app.exec_()

# ========================================================================================
if __name__ == "__main__":
	main(sys.argv)

# ========================================================================================
# END OF SCRIPT
# ========================================================================================

