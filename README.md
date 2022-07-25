---
layout: page
title: Contact Form Documentation
---

# ContactForm

This project provides a simple CGI-based contact form arranged in a format that
fits in easily with a Jekyll-based static web site. The script takes measures to
prevent casual discovery of the destination address and/or email credentials by
storing those details out of reach of the web server.

## Requirements

The script makes the following assumptions:

* that Python 3.6 or greater exists on the host and that it can be used to run
  CGI scripts under the current configuration of the web server,

* that the Python libraries named in the "import" statement at the top of the
  `contact.cgi` file (like cgi, cgitb, json, smtplib, and ssl) are installed on
  the host (most, if not all, of these should already be part of any standard
  Python installation), and

* that the web server can be configured to run CGI scripts as the owner of the
  script file rather than a generic "nobody" user (although this requirement is
  only needed in order to store secure information outside the web server root;
  if your CGI runs under a generic UID, you can still use this script but your
  secure information will be at greater risk).

## Installation

To install the contact form, copy the contents of this repository to a directory
in your Jekyll source tree, if you're using Jekyll, or to a directory in the
root directory of your website. The configuration files assume the name of the
directory is "contact" but with a bit of editing (see below) you should be able
to put the files in any directory you prefer.

The `contact-secret.json` file should be moved or copied to your $HOME directory
before filling it out with your secure information. It should also be renamed
to `contact.json`. If this is not possible, the variable settings in that file
should be copied into the `contact.json` file, which will remain in the directory
containing the `contact.cgi` file.

## Non-Jekyll Installation

Note that if you are not using Jekyll to construct your web site, you will have
to convert the `contact.md` file, and possibly the `README.md` file, to HTML.

The simplest way to accomplish that is to take a sample page from your existing
website source, delete the content of the page, and then drop the form element
from `contact.md` into the spot where the deleted content used to be. The file
should then be renamed `content.html` (or `README.html` if you are converting
the `README.md` file.

## Configuration

There are a number of simple configuration steps outlined in the subsections
below. The steps which are not marked "mandatory" are optional steps you might
want to take to customize the user experience to match your preferences.

### Setting the site name and/or preparing to serve multiple sites

(work in progress)

### Adding your secure information (mandatory)

The `contact-secret.md` file contains SMTP login data and email addresses that
you might not want web visitors to be able to access. By storing these values
in a file in the $HOME directory of the account, the file will not be visible
to the web server at all. So as long as the account directory is not hacked,
your secure information should be safe.

This file should be renamed to match the basename of the script itself (the
default basename of the script is `contact`). There is currently no provision
to support configuration files in any locaiton other than $HOME and the same
directory as the CGI script itself.

If a `contact.json` file exists in both the $HOME directory and the directory
where the CGI script itself resides, any variables set in the latter config
file will overwrite data read from the former if the key names are the same.

The `SmtpHost` and `SmtpPort` variables should be set to the host and port
where your SMTP (ie: outgoing email) server can accept logins.

The `SenderUsername` and `SenderPassword` variables should be set to the
username and password for the email account which will be sending emails on
behalf of the contact form script. If your hosting account allows for more
than one mailbox, it might be prudent to set-up a separate "contact" email
mailbox to be used exclusively for sending contact form submissions. That
way if your account *is* hacked and the intruder finds the `contact.json`
file with your secure information, the most they would be able to do is
to send email from that account -- your hosting account password would, of
course, be something different.

The `SenderEmail` variable should be set to the email address of the mailbox
from which contact form submissions will be originating. This will be used
as the "From:" address for the emails.

The `TargerEmail` variable should be set to the email address where you would
like the contact form submissions to be sent.

### Editing the script to fit your environment (possibly mandatory)

If the `python3` command invokes the Python 3.x interpreter on your host, then
the script should run as-is. If your Python command is different (ie: `python`
as opposed to `python3`), edit the first line of the script to use the proper
command.

If you have trouble with the script and want to see the data and form values
the script is receiving from the server, in addition to the values in the
environment at the time the script is run, set the `Debug` variable to `True`.

By default, the script assumes that the configuration files (in the script
directory and the $HOME directory) are both named to match the script itself
but with a `.json` extension. If you want to change the basename of the files,
there are two possibilities:

1. set the `CfgFile` variable in the script to the basename you want to use, or
1. rename the script itself (keeping the `.cgi` extension if that's required
by your web server configuration).

### Editing optional information

* DateFormat
* SenderName
* EmailSubject

12345678901234567890123456789012345678901234567890123456789012345678901234567890
