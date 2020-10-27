from configparser import ConfigParser

config = ConfigParser()

#settings section
config['settings'] = {
        'port' : 1300    
        }

#path section
config['paths'] = {
        'ServerRoot' : '/home/nikhil/Documents/CN/http_server_project',
        'DocumentRoot' : '/home/nikhil/Documents/CN/http_server_project'
        }

#file section
config['files'] = {
        'logfile' : '${paths:ServerRoot}/access.log',
        'errorfiles' : '${paths:ServerRoot}/errors_html'
        }

with open ('myserver.conf', 'w') as configfile:
    config.write(configfile)
