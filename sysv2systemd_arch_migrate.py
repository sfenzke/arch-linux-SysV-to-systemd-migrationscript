#!/usr/bin/env python2
import sys
import getopt
import os

outputDir = ''
verbose = False

def main():
	global outputDir, verbose
	
	if not os.geteuid() == 0:
		print 'Script was not invoked as root.\n' \
				'Please make sure to chown and chgrp to root the generated files before use!'

	try:
		opts, args = getopt.getopt(sys.argv[1:], 'o:vh');
		for o, a in opts:
			if o == '-o':
				if not a[-1] == '/':
					outputDir = a + '/'
				else:
					outputDir = a
			if o == '-v':
				verbose = True;
			if o == '-h':
				printHelp()	
				return 0
		parse_rc_conf()
		return 0				

	except getopt.error, message:
		print message
		print 'for help use -h'
		return 2

def debug(message):
	if verbose:
		print message

def write_conf(filename, values=None, **options):
	global outpuDir

	path = outputDir + filename

	with open(path, 'w') as conf_file:
		if not values == None:
			if not type(values) == str:
				for value in values:
					conf_file.write(value + '\n')
			else:
				conf_file.write(values + '\n')
			
		conf_file.writelines('%s=%s\n' % pair for pair in options.iteritems())
		debug('wrote ' + path)
		
def parse_rc_conf():
	global outputDir, verbose

	if outputDir == '':
		outputDir = './'

	debug('start reading rc.conf')

	rc_conf_file = open("/etc/rc.conf", "r")
	
	for line in rc_conf_file.readlines():
		line = line.rstrip("\n")
		if not line.startswith('#') and '=' in line:
			name, sep, value = line.partition('=')

			if name == 'LOCALE':
				lang = value.strip('"')
			elif name == 'KEYMAP':
				keymap = value.strip('"')
			elif name == 'CONSOLEFONT':
				consolefont = value.strip('"')
			elif name == 'CONSOLEMAP':
				fontmap = value.strip('"')
			elif name == 'HOSTNAME':
				hostname = value.strip('"')
			elif name == 'HARDWARECLOCK':
				hardwareclock = value.strip('"')
			elif name == 'TIMEZONE':
				timezone = value.strip('"')
			elif name == 'MODULES':
				modules = value.lstrip('(').rstrip(')').split()
	rc_conf_file.close()
	try:
		write_conf('hostname', values=('hostname'))
		write_conf('vconsole.conf', KEYMAP=keymap, FONT=consolefont, FONT_MAP=fontmap)
		write_conf('locale.conf', LANG=lang)
		write_conf('timezone', values=(timezone))

		if hardwareclock == 'localtime':
			write_conf('adjtime', values=('0.0 0.0 0.0\n0\nLOCAL'))

		if modules:
			modules_dirname = 'modules-load.d'
			blacklist_dirname ='modprobe.d'

			debug('creating ' + outputDir + modules_dirname)
			debug('creating ' + outputDir + blacklist_dirname)
			try:
				os.mkdir(outputDir + modules_dirname, 0755)
				os.mkdir(outputDir + blacklist_dirname, 0755)
			except OSError:
				pass

			for module in modules:
				if not module[0] == '!':
					write_conf(modules_dirname + '/' + module + '.conf', values=(module))
				else:
					module = module.lstrip('!')
					write_conf(blacklist_dirname + '/' + module + '.conf', values=('blacklist ' + module))
	except IOError as e:
		print e.strerror	

def printHelp():
	print '''This skript is intended to help migrating an arch linux installation from the old\n
sysv init system to the new systemd init.\n
This is achieved by parsing the rc.conf-file\n
from /etc and create the needed config files.\n
There are 3 options to this scricpt:\n
\t-o dir\n\t\tlets you secify an output directoy. If ommitted the 
directory this skript was invoked from will be used as output directory\n
\t-v\n\t\tmakes the skript tell you about it\'s steps\n
\t-h\n\t\tshows this help message'''

if __name__ == "__main__":
	sys.exit(main())
