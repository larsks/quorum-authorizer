=====================
quorum authentication
=====================

.. contents::

Motivation
==========

We have a system on which our normal mechanism for obtaining administrative
access depends on a network authentication mechanism that is outside of our
control.  While this mechanism offers strong security features, we wanted
to have a fallback mechanism in place that would allow us to gain
administrative privilges on the system if the network authentication system
was unavailable.

How it works
============

Registering requests
--------------------

Someone wishing to gain elevated privileges registers a request with the
``quorum`` command::

  quorum request do_something_special

Where *do_something_special* corresponds to a label in the quorum
configuration file.

Authorizing requests
--------------------

Other users on the system who wish to authorize the
request vote with the ``quorum`` command::

  quorum authorize do_something_special

Once enough votes have been registered to meet the requirements in the
configuration file, the quorum authorizer service will execute the command
defined in the configuration file.

Request lifetime
----------------

Requests must be authorized within a specific lifetime (by default, 5
minutes).  If the quorum authorizer service finds a request that has
expired, that request (and any authorizations) will be removed.

Notification
------------

The quorum authorizer service normally logs to syslog, but will also log to
*stderr* if given the ``-e`` command line flag.

Behind the scenes
=================

The quorum authorizer service watches a directory (by default
``/var/lib/quorum``).  Authentication requests are logged by creating a
directory inside this directory.  Authorizations are registered by creating
files inside of the request directory.

Votes are tallied by user id. That is, even if the same user creates
multiple files in the request directory, they will only get a single vote.

The quorum authorizer service is designed to be run minutely out of cron:

  * * * * * /usr/bin/quorum-authorizer > /dev/null 2>&1


Configuration
=============

The default quorum configuration file is ``/etc/quorum/quorum.ini``.  This
can be overridden with the ``-f`` command line option or with the
``QUORUM_CONFIG`` environment variable.  The file is a typical .ini style
configuration file.

The quorum section
------------------

There is one required section, ``quorum``, which may be empty.  You may set
the following configuration items here:

- ``request directory`` -- where to look for requests.
- ``valid for`` -- how long requests are valid for before they are expired.

For example::

  [quorum]

  request directory = /var/lib/quorum

Command definitions
-------------------

There may be zero or more command definitions, each in a configuration
section named 'command *command_name*'.  In each command definition you may
se the following items:

- ``command`` -- the shell command to execute when a corresponding request
  is authorized.
- ``run as`` -- the user id under which the command should run.
- ``required votes`` -- how many votes are required to authorize this
  command.

For example::

  [command sample]

  command = touch /tmp/sample.command
  run as = root
  required votes = 2

The DEFAULT section
-------------------

Any configuration item that can be set in a command definition can also be
provided in the DEFAULT section, where it will used as the default commands
that do not otherwise override the value.

For example::

  [DEFAULT]

  required votes = 2

Installing
==========

You may install this using the ``setup.py`` script included in the
distribution::

  python setup.py install

You may also be able to build a binary package for your platform of choice.
For example::

  python setup.py bdist_rpm

This will place an RPM in ``dist/`` subdirectory.

Post-installation tasks
-----------------------

After installing the package you will need to complete the following tasks.

#. After installing the package you will need to place a configuration file
   in ``/etc/quorum/quorum.ini``.  There is an example file included in the
   distribution.

#. You will need to create the request directory, typically
   ``/var/lib/quorum``.  You will need to set appropriate permissions on
   this directory so that users who need to authorize requests will be able
   to create directories here.


