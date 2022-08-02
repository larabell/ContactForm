#!/usr/bin/env python3
#
# Copyright 2022 Joseph L Larabell
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# =====
#
# Requires: Python 3.6 or greater and those modules listed in the import command
#

import cgi, cgitb, datetime, getpass, html, json, os, re, requests, smtplib, ssl, string, sys, traceback

#
# Set to True in order to have the script emit enhanced error and debug information
#
Debug = False

#
# Set to the basename of the configuration file(s)... default: basename of script
#
CfgFile = os.path.splitext(os.path.basename(sys.argv[0]))[0]

###
### NO user-modifiable settings beyond this point
###

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

			if os.path.exists(cfgfile):
				with open(cfgfile, 'r') as cfg:
					data = json.load(cfg)

					# If 2nd path component is present, look-up the corresponding configuration object

					config.update(data[pathinfo[1]] if len(pathinfo) > 1 else data)

		return config

	except Exception as ex:
		sendError('Cannot read configuration file: {0}'.format(cfgfile), ex)

	return None

def getDataValues(config, formData):
	values = {'Date': datetime.datetime.now().isoformat(sep = ' ')}

	# Use ISO8601 format for timestamp unless configured otherwise

	if 'DateFormat' in config:
		values['Date'] = datetime.datetime.now().strftime(config['DateFormat'])
	else:
		values['Date'] = datetime.datetime.now().isoformat(sep = ' ')

	if 'Fields' in config:
		fields = config['Fields']

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

	return values

def composeMessage(config, values):

	sender  = config['SenderName']   if 'SenderName'   in config else 'Contact Form'
	address = config['SenderEmail']  if 'SenderEmail'  in config else 'contact'
	subject = config['EmailSubject'] if 'EmailSubject' in config else 'Contact Form Submission'

	headers = '\n'.join([
		'From: "{0}" <{1}>'.format(sender, address),
		'Subject: {0}'.format(subject)
	])

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

	# Headers are separated from message body by a single blank line

	return '\n'.join([headers, msg.substitute(values)])

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

	try:
		with smtplib.SMTP(config['SmtpHost'], config['SmtpPort']) as server:
			server.starttls(context = context)

			server.login(config['SenderUsername'], config['SenderPassword'])

			message = composeMessage(config, values)

			server.sendmail(config['SenderEmail'], config['TargetEmail'], message)

	except Exception as ex:
		sendError('Cannot send email... check your configuration', ex)

###
### MAIN ROUTINE
###

# Emit HTML header (so we can easily emit errors if necessary)

print('Content-type: text/html\n\n')

# Enable debug if requested

cgitb.enable(display = Debug)

formData = cgi.FieldStorage(encoding = 'utf-8')

# Read JSON config file

configData = getConfiguration()

# Process form fields

formValues = getDataValues(configData, formData)

# Verify the reCAPTCHA, if configured

recaptchaResponse = formData.getfirst('g-recaptcha-response', None)

if recaptchaResponse and 'RecaptchaKey' in configData:
	url = 'https://www.google.com/recaptcha/api/siteverify'

	obj = {
		'secret':   configData['RecaptchaKey'],
		'response': recaptchaResponse,
		'remoteip': os.environ.get('REMOTE_HOST')
	}

	response = requests.post(url, data = obj)

	success = 'Passed' if response.json().get('success') else 'Failed'

else:
	success = 'Skipped' # reCAPTCHA wasn't used

# Log the request, if configured

if 'Logfile' in configData:
	timestamp = datetime.datetime.now().isoformat()

	values = '{' + ', '.join(['"{0}": {1}'.format(key, formData.getlist(key)) for key in formData]) + "}"

	with open(configData['Logfile'], 'a') as log:
		log.write('{0} [{1}] {2} {3}\n'.format(timestamp, success, os.environ.get('REQUEST_URI'), values))

# Send email message unless reCAPTCHA failed

if success in ['Passed', 'Skipped']:
	sendMail(configData, formValues)

# Generate HTML response page from template

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

