#!/usr/bin/env python
# Ian Rees, 2012
# Edited by Stephen Murray 2014
# This is a new version of the EMAN2 build and post-install package management system.
# The original version was a collection of shell scripts, with various scripts for
# setting configuration information, CVS checkout, build, package, upload, etc., run
# via a cron job. 
#
# This script expects the following directory layout:
# 
#   <target>/
#       co/
#           <cvsmodule>.<release>/                               EMAN2 source from CVS, e.g. "eman2.daily", "eman2.EMAN2_0_5"
#       local/                
#           [lib,bin,include,doc,share,qt4,...]                  PREFIX for dependency library installs -- think /usr/local
#       extlib/
#           <cvsmodule>.<release>/[lib,bin,site-packages,...]    Stripped down copy of local/ that only includes required libraries.
#       build/
#           <cvsmodule>.<release>/                               CMake configure and build directory
#       stage/
#           <cvsmodule>.<release>/                               Staging area for distribution
#               EMAN2/[bin,lib,extlib,...]                       EMAN2 installation
#       images/                                                  Completed, packaged distributions
#

import os
import sys
import re
import shutil
import subprocess
import glob
import datetime
import argparse
import platform

##### Helper functions #####

def log(msg):
	"""Print a message."""
	print "=====", msg, "====="

def find_exec(root='.'):
	"""Find executables (using +x permissions)."""
	# find . -type f -perm +111 -print
	p = check_output(['find', root, '-type', 'f', '-perm', '+111'])
	# unix find may print empty lines; strip those out.
	return filter(None, [i.strip() for i in p.split("\n")])

def find_ext(ext='', root='.'):
	"""Find files with a particular extension. Include the ".", e.g. ".txt". """
	found = []
	for root, dirs, files in os.walk(root):
		found.extend([os.path.join(root, i) for i in files if i.endswith(ext)])
	return found

def mkdirs(path):
	"""mkdir -p"""
	if not os.path.exists(path):
		os.makedirs(path)
  
def rmtree(path):
	"""rm -rf"""
	if os.path.exists(path):
		shutil.rmtree(path)

def retree(path):
	"""rm -rf; mkdir -p"""
	if os.path.exists(path):
		shutil.rmtree(path)
	if not os.path.exists(path):
		os.makedirs(path)  
	
def cmd(*popenargs, **kwargs):
	print "Running:", 
	print " ".join(*popenargs)
	kwargs['stdout'] = subprocess.PIPE
	kwargs['stderr'] = subprocess.PIPE
	process = subprocess.Popen(*popenargs, **kwargs)
	# 
	a, b = process.communicate()
	exitcode = process.wait()
	if exitcode:
		print("WARNING: Command returned non-zero exit code: %s"%" ".join(*popenargs))
		print a
		print b
	
def echo(*popenargs, **kwargs):
	print " ".join(popenargs)    
	
def check_output(*popenargs, **kwargs):
	"""Copy of subprocess.check_output()"""
	if 'stdout' in kwargs:
		raise ValueError('stdout argument not allowed, it will be overridden.')
	process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
	output, unused_err = process.communicate()
	retcode = process.poll()
	if retcode:
		cmd = kwargs.get("args")
		if cmd is None:
			cmd = popenargs[0]
		raise subprocess.CalledProcessError(retcode, cmd)            
	return output

##### Targets #####

class Target(object):
	"""Target-specific configuration and build commands.
	
	Each target defines some configuration for that platform, and the 
	methods checkout, build, install, upload, etc., can be customized to 
	list the actions required for each platform.
	"""

	# Used in the final archive filename
	target_desc = 'source'

	def __init__(self, args):
		# Find a nicer way of doing this. I just want to avoid excessive duplicate os.join()
		# calls in the main code, because each one is a chance for an error.        
		args.cwd_co            = os.path.join(args.root, 'co')
		args.cwd_co_distname   = os.path.join(args.root, 'co',   args.distname)
		args.cwd_extlib        = os.path.join(args.root, 'extlib',  args.distname)
		args.cwd_build         = os.path.join(args.root, 'build',   args.distname)
		args.cwd_images        = os.path.join(args.root, 'images',  args.distname)
		args.cwd_images_source = os.path.join(args.root, 'images',  args.distname_source)
		args.cwd_stage         = os.path.join(args.root, 'stage',   args.distname)
		args.cwd_stage_source  = os.path.joi    n(args.root, 'stage',   args.distname_source)
		args.cwd_stage_source_build = os.path.join(args.root, 'stage',  args.distname_source,'EMAN2/src/build')
		args.cwd_stage_source_path  = os.path.join(args.root, 'stage',   args.distname_source,'EMAN2/src/eman2')
		args.cwd_rpath         = os.path.join(args.root, 'stage',   args.distname, args.cvsmodule.upper())
		args.cwd_rpath_source  = os.path.join(args.root, 'stage',   args.distname_source, args.cvsmodule.upper(),'src/eman2')
		args.cwd_rpath_extlib  = os.path.join(args.cwd_rpath, 'extlib')
		args.cwd_rpath_lib     = os.path.join(args.cwd_rpath, 'lib')           

		# OS X links using absolute pathnames; update these to @rpath macro.
		# This dictionary contains regex sub keys/values that will be used 
		# to process the output from otool -L.

		args.replace = {
			# The basic paths
			'^%s/local/'%(args.root): '@rpath/extlib/',
			'^%s/build/%s/'%(args.root, args.distname): '@rpath/',
			# Boost's bjam build doesn't set install_name
			'^libboost_python.dylib': '@rpath/extlib/lib/libboost_python.dylib',
			# Same with EMAN2.. for now..
			'^libEM2.dylib': '@rpath/lib/libEM2.dylib',
			'^libGLEM2.dylib': '@rpath/lib/libGLEM2.dylib',
		}

		self.args = args
	
	def _run(self, commands):
		# Run a series of Builder commands
		for c in commands:
			c(self.args).run() # pass the args Namespace to the Builder.

	def run(self, commands):
		for i in commands:
			getattr(self, i)()
	
	def fix(self):
		self._run([FixLinks, FixInstallNames])
	
class Mac64Target(Target):
	"""Generic Mac target."""
	target_desc='mac-64'

	def fix(self):
		self._run([FixLinks, FixInstallNames])

class Linux32Target(Target):
	target_desc = 'linux-32'
	def fix(self): 
		self._run([FixLinuxRpath])
		   
class Linux64Target(Linux32Target):
	target_desc = 'linux-64'
	pass
	
##### Builder Modules #####

class Builder(object):
	"""Build step."""
	
	def __init__(self, args):
		# Reference to Target configuration args Namespace
		self.args = args
	
	#@abstractmethod
	def run(self):
		"""Each builder class must implement run()."""
		return NotImplementedError

# Mac specific build sub-command.
class FixLinks(Builder):
	def run(self):
		log("Creating .dylib -> .so links for Python")
		cwd = os.getcwd() # Need to set the current working directory for os.symlink
		os.chdir(self.args.cwd_rpath_lib)
		for f in glob.glob("*.dylib"):
			try: os.symlink(f, f.replace(".dylib", ".so"))
			except: pass
		os.chdir(cwd)

# Set rpath $ORIGIN so LD_LIBRARY_PATH is not needed on Linux.
# This should work on all modern Linux systems.
class FixLinuxRpath(Builder):
	def run(self):
		log("Fixing rpath")
		targets = set()
		targets |= set(find_ext('.so', root=self.args.cwd_rpath))
		targets |= set(find_ext('.dylib', root=self.args.cwd_rpath))
		targets |= set(find_exec(root=self.args.cwd_rpath))

		for target in sorted(targets):
			if ".py" in target:
				continue
			xtarget = target.replace(self.args.cwd_rpath, '')
			depth = len(xtarget.split('/'))-2
			origins = ['$ORIGIN/']
			base = "".join(["../"]*depth)
			for i in ['extlib/lib']:
				origins.append('$ORIGIN/'+base+i+'/')
			try:
				cmd(['patchelf', '--set-rpath', ":".join(origins), target])
			except Exception, e:
				print "Couldnt patchelf:", e        

# Mac specific build sub-command. 
class FixInstallNames(Builder):
	"""Process all binary files (executables, libraries) to rename linked libraries."""
	
	def find_deps(self, filename):
		"""Find linked libraries using otool -L."""
		p = check_output(['otool','-L',filename])
		# otool doesn't return an exit code on failure, so check..
		if "not an object file" in p:
			raise Exception, "Not Mach-O binary"
		# Just get the dylib install names
		p = [i.strip().partition(" ")[0] for i in p.split("\n")[1:]]
		return p

	def id_rpath(self, filename):
		"""Generate the @rpath for a file, relative to the current directory as @rpath root."""
		p = len(filename.split("/"))-1
		f = os.path.join("@loader_path", *[".."]*p)
		return f

	def run(self):
		log("Fixing install_name")
		cwd = os.getcwd()
		os.chdir(self.args.cwd_rpath)       
 
		# Find all files that end in .so/.dylib, or are executable
		# This will include many script files, but we will ignore
		# these failures when running otool/install_name_tool
		targets = set()
		targets |= set(find_ext('.so', root=self.args.cwd_rpath))
		targets |= set(find_ext('.dylib', root=self.args.cwd_rpath))
		targets |= set(find_exec(root=self.args.cwd_rpath))

		for f in sorted(targets):
			# Get the linked libraries and
			# check if the file is a Mach-O binary
			try:
				libs = self.find_deps(f)
			except Exception, e:
				continue

			# Strip the absolute path down to a relative path
			frel = f.replace(self.args.cwd_rpath, "")[1:]

			# Set the install_name.
			install_name_id = os.path.join('@rpath', frel)
			# print "\tsetting id:", install_name_id
			cmd(['install_name_tool', '-id', install_name_id, f])

			# Set @rpath, this is a reference to the root of the package.
			# Linked libraries will be referenced relative to this.
			rpath = self.id_rpath(frel)
			# print "\tadding @rpath:", rpath
			try: cmd(['install_name_tool', '-add_rpath', rpath, f])
			except: pass

			# Process each linked library with the regexes in REPLACE.
			for lib in libs:
				olib = lib
				for k,v in self.args.replace.items():
					lib = re.sub(k, v, lib)
				if olib != lib:
					# print "\t", olib, "->", lib
					try: cmd(['install_name_tool', '-change', olib, lib, f])
					except: pass

##### Registry #####

TARGETS = {
	'osx-64': Mac64Target,
	'linux-32': Linux32Target,
	'linux-64': Linux64Target
}

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--prefix', help='Installation root (Anaconda PREFIX)', required=True, dest="root")
	parser.add_argument('--dist',   help='Full name of EMAN2 binary', required=True, dest="distname")
	parser.add_argument('--target', choices=['osx-64','linux-32','linux-64'], required=True)
	args = parser.parse_args()
	
	args.date = datetime.datetime.utcnow().isoformat()
	args.python = sys.executable

	print("System info:")
	print("Target: \t{}".format(args.target))
	print("Distrib:\t{}".format(args.distname))
	print("Prefix: \t{}".format(args.root))
	print("Python: \t{}".format(args.python))
	print("Date:   \t{}".format(args.date))

	target = TARGETS.get(args.target, Target)(args)
	target.run(["fix"])
