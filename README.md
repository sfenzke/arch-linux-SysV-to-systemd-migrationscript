This is a little python2-script intended to help you migrate from a legacy arch linux installation to an pure systemd arch linux installation.
The script will parse your /et/rc.conf and generate the config files needed by systemd for you. Your real configuration won't be touched, 
the generated files will be put in the folder from where this script was invoked. Optionnally you can give an output directory with the -o parameter.
For further help run the script with -h option.
