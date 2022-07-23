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
  <code>contact.cgi<code> file (like cgi, cgitb, json, smtplib, and ssl) are
  installed on the host (most of these should already be part of any standard
  Python installation), and

* that the web server can be configured to run CGI scripts as the owner of the
  script file rather than a generic "nobody" user (although this requirement is
  only needed in order to store secure information outside the web server root;
  if your CGI runs under a generic UID, you can still use this script but your
  secure information will be at greater risk).

## Installation

(work in progress)

## Configuration

(work in progress)

12345678901234567890123456789012345678901234567890123456789012345678901234567890
