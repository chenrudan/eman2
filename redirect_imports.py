#!/usr/bin/env python

import os
import errno
import shutil

progs_contain = ["em","EM","libpy","EMAN","eman","e2"]
bindir_files = [i.replace(".py","") for i in os.listdir("./programs")]

#homedir = os.getenv("HOME")
#bindir_files = [i.replace(".py","") for i in os.listdir(homedir+"/src/eman2-conda/programs")]

def main():
	olddir = os.getcwd()
	newdir = "../{}_refactor".format(os.path.basename(olddir))

	global bindir_files
	bindir_files = [i.replace(".py","") for i in os.listdir("./programs")]

	for root,dirs,files in os.walk(olddir,topdown=True):
		print("\n\nCWD: {}\n\n".format(root))

		newroot = root.replace(olddir,newdir)
		mkdir_p(newroot)

		for f in files:
			if os.path.isfile("{}/{}".format(root,f)):
				if f[-3:] == ".py":
					with open("{}/{}".format(root,f),'r') as inf:
						file_content = inf.read()
					file_content = fix_imports(file_content)
					with open("{}/{}".format(newroot,f),'w') as outf:
						outf.write(file_content)
				else:
					try: shutil.copy("{}/{}".format(root,f),"{}/{}".format(newroot,f))
					except: pass

	print("Results stored in: {}".format(newdir))

def mkdir_p(path):
	try: os.makedirs(path)
	except OSError as exc:
		if exc.errno == errno.EEXIST and os.path.isdir(path): pass
		else: raise

def fix_imports(lines):
	for l in lines.split("\n"):
		if l != "" and l.strip() != "": # we don't care about blank lines
			if l.strip()[0] != "#": # we don't want whole line comments
				if "import " in l and l.strip()[0] != "#": # is this an import statement?
					if any(s in l for s in progs_contain):  # is this an EMAN2 program
						if '"""' not in l and "=" not in l and "print" not in l: # import statements don't contain = or multiline comments.
							if len(l) < 500: #They're also relatively short.
								old = l.strip()
								new = get_new_import(old)
								l.replace(old,new)
	return lines.join("\n")+"\n"

def insert(s,i,x):
	return s[:x]+i+s[x:]

def get_new_import(imp):
	#oldimp = oldimp.split("#")[0]
	print(imp)

	if "try:" in imp: oldimp = imp.replace("try: ","") # remove "try: " from try/except import lines
	else: oldimp = imp

	oldimp = " ".join(oldimp.split()) # some people seem to add extra spaces in their imports

	if "." in oldimp or ".." in oldimp: newimp = oldimp # leave relative imports alone. pretty sure we want them as-is.
	else:
		if oldimp.find("from") == 0: # case 1: from
			if oldimp != "from EMAN2 import *":
				if "from EMAN2 import" in oldimp:
					newimp = oldimp
				else:
					if oldimp.split(" ")[1] in bindir_files:
						newimp = oldimp # program in bin, so import doesn't need to be altered
					else:
						newimp = insert(oldimp,"EMAN2.",len("from ")) # replace "from module" with "from EMAN2.module"
			else: newimp = oldimp
		elif oldimp.find("import") == 0: # case 2: import
			if oldimp == "import EMAN2": # we just use the existing import
				newimp = oldimp
			else:
				if oldimp.split(" ")[1] in bindir_files:
					newimp = oldimp
				elif " as " in oldimp:
					newimp = insert(oldimp,"EMAN2.",len("import ")) # replace "import module as x" with "import EMAN2.module as x"
				else:
					newimp = "import EMAN2.{module} as {module}".format(module=oldimp.replace("import ","")) # replace "import module" with "import EMAN2.module"
		else: newimp = oldimp # otherwise
	if "try" in imp: newimp = "try: " + newimp # add "try" back to try/except imports

	print("\t{}".format(newimp))
	return newimp


if __name__ == "__main__":
	main()
