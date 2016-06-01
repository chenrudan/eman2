#!/usr/bin/env python

# Original build.py script by Ian Rees, 2012. Edits by Stephen Murray, 2014.
# Modified for Anaconda (fix-libs.py) by Michael Bell, 2016
#

import os
import sys
import re
import subprocess
import glob
import datetime
import argparse

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--prefix', help='Installation root (Anaconda PREFIX)', required=True, dest="root")
	parser.add_argument('--dist',   help='Full name of EMAN2 binary', required=True, dest="distname")
	parser.add_argument('--target', choices=['osx-64','linux-32','linux-64'], required=True)
	args = parser.parse_args()
	
	args.date = datetime.datetime.utcnow().isoformat()
	args.python = sys.executable
	args.cwd_rpath = os.path.join(args.root,'lib/python2.7/site-packages/EMAN2')

	if 'osx' in args.target:
		target = MacTarget(args)
	elif "linux" in args.target:
		target = LinuxTarget(args)

	target.run(["fix"])

##### Helper functions #####

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

def cmd(*popenargs, **kwargs):
	print("Running:\n{}".format(" ".join(*popenargs)))
	kwargs['stdout'] = subprocess.PIPE
	kwargs['stderr'] = subprocess.PIPE
	process = subprocess.Popen(*popenargs, **kwargs)
	a, b = process.communicate()
	exitcode = process.wait()
	if exitcode: print("WARNING: Command returned non-zero exit code: {}\n{}\n{}".format(" ".join(*popenargs),a,b))

def check_output(*popenargs, **kwargs):
	"""Copy of subprocess.check_output()"""
	if 'stdout' in kwargs:
		raise ValueError('stdout argument not allowed, it will be overridden.')
	process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
	output, unused_err = process.communicate()
	retcode = process.poll()
	if retcode:
		cmd = kwargs.get("args")
		if cmd is None: cmd = popenargs[0]
		raise subprocess.CalledProcessError(retcode, cmd)            
	return output

##### Fixer Modules #####

class Fixer(object):
	"""Generic shared library fixer object."""
	
	def __init__(self, args):
		# Reference to Target configuration args Namespace
		self.args = args
	
	def run(self):
		"""Each fixer class must implement run()."""
		return NotImplementedError

##### Mac specific fixers.

class FixLinks(Fixer):
	"""Creates .dylib -> .so links for python"""

	def run(self):
		cwd = os.getcwd() # Need to set the current working directory for os.symlink
		os.chdir(self.args.cwd_rpath)
		for f in glob.glob("*.dylib"):
			try: os.symlink(f, f.replace(".dylib", ".so"))
			except: pass
		os.chdir(cwd)  

class FixInstallNames(Fixer):
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
			try: libs = self.find_deps(f)
			except Exception, e: continue

			# Strip the absolute path down to a relative path
			frel = f.replace(self.args.cwd_rpath, "")[1:]

			# Set the install_name.
			install_name_id = os.path.join('@rpath', frel)
			# print "\tsetting id:", install_name_id
			cmd(['install_name_tool', '-id', install_name_id, f])

			# Set @rpath, this is a reference to the root of the package.
			# Linked libraries will be referenced relative to this.
			rpath = self.id_rpath(frel)
			try: cmd(['install_name_tool', '-add_rpath', rpath, f])
			except: pass

			# Process each linked library with the regexes in REPLACE.
			for lib in libs:
				olib = lib
				for k,v in self.args.replace.items():
					lib = re.sub(k, v, lib)
				if olib != lib:
					try: cmd(['install_name_tool', '-change', olib, lib, f])
					except: pass

##### Linux specific fixes

class FixLinuxRpath(Fixer):
	"""Set rpath $ORIGIN so LD_LIBRARY_PATH is not needed on Linux. This should work on all modern Linux systems."""
	
	def run(self):
		targets = set()
		targets |= set(find_ext('.so', root=self.args.cwd_rpath))
		targets |= set(find_ext('.dylib', root=self.args.cwd_rpath))
		targets |= set(find_exec(root=self.args.cwd_rpath))

		for target in sorted(targets):
			if ".py" in target: continue
			xtarget = target.replace(self.args.cwd_rpath, '')
			depth = len(xtarget.split('/'))-2
			origins = ['$ORIGIN/']
			#base = "".join(["../"]*depth)
			#for i in ['extlib/lib']:
			#	origins.append('$ORIGIN/'+base+i+'/')
			try: cmd(['patchelf', '--set-rpath', ":".join(origins), target])
			except Exception, e: print("Couldnt patchelf: {}".format(e))      

##### Targets #####

class Target(object):
	"""Target-specific configuration for modifying shared libraries."""

	def __init__(self, args):
		self.args = args
	
	def run(self, commands):
		for i in commands:
			getattr(self, i)()
	
	def fix(self):
		"""Run a series of Fixer commands"""
		for c in self.fixers:
			c(self.args).run() # pass the args Namespace to the Fixer.

class MacTarget(Target):
	"""Mac-specific configuration for modifying shared libraries."""
	fixers = [FixLinks,FixInstallNames]

	def __init__(self, args):
		# OS X links using absolute pathnames; update these to @rpath macro.
		# This dictionary contains regex substitutions for "otool -L".
		args.replace = {
			'^{}'.format(args.root): '@rpath/',
			'^libEM2.dylib': '@rpath/lib/python2.7/site-packages/EMAN2/libEM2.dylib',
			'^libGLEM2.dylib': '@rpath/lib/python2.7/site-packages/EMAN2/libGLEM2.dylib'
		}
		self.args = args

class LinuxTarget(Target):
	"""Linux-specific configuration for modifying shared libraries."""
	fixers = [FixLinuxRpath]
	
if __name__ == "__main__":
	main()
