#!/usr/bin/env python3
#
# Requires: Python 3.6 or greater and those modules listed in the import command
#
# ToDo:
#   o Table for incoming fields and required flags
#   o Configuration from a file
#     o Form field table
#   o Secret field to dump environment (must match setting in config file)
#   o Adjustable data format
#

import cgi, cgitb, datetime, getpass, html, json, os, re, smtplib, ssl, string, sys, traceback

Debug = True

CfgFile = os.path.splitext(os.path.basename(sys.argv[0]))[0]

def printDebugBlock():
	print('<pre>')

	print('Script running as user: "{0}" in "{1}"'.format(getpass.getuser(), os.getcwd()))
	print('Config file basename is: "{0}"'.format(CfgFile))

	print('--- Environment ---')

	for var in os.environ:
		print('{0}: {1}'.format(var, html.escape(os.environ[var])))

	print('--- Form Data ---')

	if formValues:
		keylen = max([len(key) + 2 for key in formValues.keys()])

		for key in formValues.keys():
			print('{0:<{width}}{1}'.format(key + ': ', html.escape(formValues.get(key, '(null)')), width = keylen))

	else:
		print('** No Form Data **')

	print('--- Config Data ---')

	if configData:
		print(html.escape(json.dumps(configData, indent = 4)))

	else:
		print('** No Config Data **')

	print('</pre>')

def sendError(message, ex = None):
	print("<h1>Error</h1><p>{0}</p>".format(html.escape(message)))

	if ex:
		print('<pre>')
		print('<br/>\n'.join(traceback.format_exception(*sys.exc_info())))
		print('</pre>')

	if Debug:
		printDebugBlock()

	sys.exit(0)

def getConfiguration():
	pathinfo = os.environ['PATH_INFO'].split('/')

	try:
		config = { }

		# Look for <1stPathInfo>.json in: (a) current directory, and (b) $HOME directory

		for path in ['.', '~']:
			cfgfile = os.path.expanduser('{0}/{1}.json'.format(path, CfgFile))

			with open(cfgfile, 'r') as cfg:
				data = json.load(cfg)

				# If 2nd path component is present, look-up the corresponding configuration object

				config.update(data[pathinfo[1]] if len(pathinfo) > 1 else data)

		return config

	except Exception as ex:
		sendError('Cannot read configuration file: {0}'.format(cfgfile), ex)

	return None

def getDataValues(config):
	formData = cgi.FieldStorage(encoding = 'utf-8')

#      "Name":    { "form": "Name",    "required": true        },
#      "Email":   { "form": "Email",   "required": true        },
#      "FormURL": { "form": "FormURL"                          },
#      "Subject": { "form": "Subject", "default": "No Subject" },
#      "Message": { "form": "Message", "default": "No Message" },
#
#      "Referer": { "env": "HTTP_REFERER" },
#      "RemHost": { "env": "REMOTE_HOST"  },
#      "Request": { "env": "REQUEST_URI"  }

	values = {'Date': datetime.datetime.now().isoformat(sep = ' ')}

	if 'Fields' in config:
		fields = config.get('Fields')

		reqFields = [field for field in fields if fields[field].get('form') and fields[field].get('required')]

		for reqField in reqFields:
			if reqField not in formData:
				sendError('Please fill in the required fields ({0}).'.format(', '.join(reqFields)))

		for field in fields:
			fieldDef = fields[field]

			if 'env' in fieldDef:
				values[field] = os.environ.get(fieldDef['env'], fieldDef.get('default', ''))

			if 'form' in fieldDef:
				values[field] = formData.getfirst(fieldDef['form'], fieldDef.get('default', ''))

	else:
		sendError('No fields are listed in the configuration file.')

#	values = {
#		'Date':    datetime.datetime.now().isoformat(sep = ' '),
#
#		'Name':    formData.getfirst('Name'),
#		'Email':   formData.getfirst('Email'),
#		'FormURL': formData.getfirst('FormURL'),
#		'Subject': formData.getfirst('Subject', 'No Subject'),
#		'Message': formData.getfirst('Message', 'No Message'),
#
#		'Referer': os.environ['HTTP_REFERER'],
#		'RemHost': os.environ['REMOTE_HOST'],
#		'Request': os.environ['REQUEST_URI']
#	}

	return values

def composeMessage(subject, config, values):

	# Use message body defined in configuration or a generic message body by default

	if 'EmailBody' in config:
		msg = string.Template('\n'.join(config['EmailBody']))

	else:
		msg = string.Template('\n'.join([
			'The following message was submitted via the contact form:',
			'',
			'Metadata:',
			'  Name:        $Name',
			'  Email:       $Email',
			'  Subject:     $Subject',
			'  Referer:     $Referer',
			'  Remote Host: $RemHost',
			'',
			'$Message'
			'',
			'++++',
			'Default message sent by Contact CGI form ($Request) on or about $Date.',
		]))

	return 'Subject: {0}\n\n'.format(subject) + msg.substitute(values)

def composeReply(config, values):

	# Use message body defined in configuration or a generic message body by default

	if 'ReplyBody' in config:
		msg = string.Template('\n'.join(config['ReplyBody']))

	else:
		msg = string.Template('\n'.join([
			'<p>This is a test reply page generated by the contact form script. The',
			'   following data items were captured by the form:',
			'',
			'<table>',
			'<tr><td>Name</td>       <td>$Name</td></tr>',
			'<tr><td>Email</td>      <td>$Email</td></tr>',
			'<tr><td>Message</td>    <td>$Message</td></tr>',
			'<tr><td>Subject</td>    <td>$Subject</td></tr>',
			'<tr><td>Referer</td>    <td>$Referer</td></tr>',
			'<tr><td>Remote Host</td><td>$RemHost</td></tr>',
			'</table>',
			'',
			'<hr>',
			'Default reply sent by Contact CGI form ($Request) on or about $Date.',
		]))

	return msg.substitute(values)

def sendMail(config, values):
	context = ssl.create_default_context()

	with smtplib.SMTP(config['SmtpHost'], config['SmtpPort']) as server:
		server.starttls(context = context)

		server.login(config['SenderUsername'], config['SenderPassword'])

		message = composeMessage('Contact Form Submission', config, values)

		server.sendmail(config['SenderEmail'], config['TargetEmail'], message)

###
### MAIN ROUTINE
###

# Emit HTML header (so we can easily emit errors if necessary)

print('Content-type: text/html\n\n')

# Enable debug if requested

cgitb.enable(display = Debug)

# Read JSON config file

configData = getConfiguration()

# Process form fields

formValues = getDataValues(configData)

# Send email message

sendMail(configData, formValues)

# Generate HTML page from template

htmlfile = configData['Template'] if 'Template' in configData else CfgFile + '.html'

try:
	with open(htmlfile, 'r') as file:
		head = re.split('<form(\s+[^>]*)?>', file.read(), maxsplit = 1)

		if len(head) > 1:
			tail = re.split('</form\s*>', head[-1], maxsplit = 1)

			if len(tail) > 1:
				print(head[0])

				print(composeReply(configData, formValues))

				# Print various values and data structures if Debug mode is enabled

				if Debug:
					printDebugBlock()

				print(tail[-1])

			else:
				sendError('Reply template file is improperly formatted, no </form> tag found')

		else:
			sendError('Reply template file is improperly formatted, no <form> tag found')

except Exception as ex:
	sendError('Cannot read template file: {0}'.format(htmlfile), ex)
