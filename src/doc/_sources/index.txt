.. CAS documentation master file, created by
   sphinx-quickstart on Wed May  6 22:44:40 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Core Analysis System
====================

:Author: Adam Stokes
:Release: |release|
:Date: |today|

Introduction
------------

.. image:: cas_logo.png

Description
^^^^^^^^^^^

CAS provides a user the ability to configure an environment for core analysis
quickly. All the hassles of matching kernel versions and machine architecture 
types to core dumps are automatically detected and processed. 

Prerequisites
^^^^^^^^^^^^^

CAS needs at least **Python 2.3** to run. For systems that are not running
Fedora 9 or later (this would include RHEL 4/5) the EPEL repo needs to be 
installed. Visit `EPEL <https://fedoraproject.org/wiki/EPEL>`_ to enable
this repository.

The amount of storage needed can be determined base on the following
information:

- The number of kernel-debuginfo packages needed
- How many core dumps will be processed.

Typically it is recommended to have at least 1TB for cores and another 500GB for
the debuginfo packages.

Since analyzing cores requires the same architecture specific systems the core 
was generated on there will need to be systems available of those same types
in order for analyzation to work properly.

Configuration
^^^^^^^^^^^^^

CAS comes with one main configuration file which is located at ``/etc/cas.conf``.
The overall contents of this file is shown below, further down we will break up
each section and describe its meaning::

    [settings]
    casuser=root
    kernels=/mnt/kernels
    rpmFilter=.*kerne.+-debuginfo-[0-9].*\.rpm
    debugs=/cores/debugs
    debugLevel=DEBUG
    workDirectory=/cores/processed
    smtphost=mail.example.com
    database=/var/db/cas/cas.db
    [maintenance]
    purgeLimit=90
    autoPurge=Yes
    [advanced]
    # crash_32=/usr/local/i386/crash
    # buffersize=None

``casuser``: (**Required**) User to run cas, recommended to run as someone other than root.

``kernels``: (**Required**) Describes the location of where kernel-debuginfo packages are to be
stored. This can range anywhere from an nfs mount, samba share, local disk or
any other type of media the cas server can access.

``rpmFilters``: (**Required**) This is a emacs based regular expression which is essentially
passed to a find command to locate the various kernel-debuginfo packages defined
in ``kernels`` directive.

``debugs``: (**Required**) A temporary directory in which to store the extracted vmlinux files
from the kernel-debuginfo packages for processing. Another solution would be to
alter this to point an existing directory like ``/tmp``, for instance.

``debugLevel``: As the name suggest it will set the debug level for CAS output.
Currently the only accepted values are ``DEBUG|INFO``.

``workDirectory``: (**Required**) Defines where all processed cores will be placed. This mount
point will need to have the most storage assigned to it. Depending on how many
cores are processed in a given timeframe this area will fill up quickly.

``smtphost``: If wanting output of CAS processing email to a certain address
this directive needs to be set. ``Note`` that the mail server should not
require smtp authentication.

``database``: (**Required**) Define where the sqlite database will reside.

``purgeLimit``: Define amount of day(s) back wish to keep physical data on
system.

``autoPurge``: Yes/No setting if wanting cas-admin to auto purge stale data on
each run.

``crash_32``: Primarily used on x86_64 systems to process x86 cores. If x86
version of crash is installed this directive can be set to the crash binary
and CAS will automatically process x86 cores on a x86_64 machine. ``Note`` this
is only available if the CAS server is a x86_64 machine.

``buffersize``: Extend the read buffer when analyzing a core for a timestamp.
``Note`` this is normally needed for itanium cores, otherwise, the default is
fine.

Setup & Execution
-----------------

Preparing CAS Server
^^^^^^^^^^^^^^^^^^^^

To install the CAS package simply type::

    $ yum install cas

Once installed edit ``/etc/cas.conf`` as root using any preferred text editor.
As described above the required directives need to be altered to suit the
environment in question.

In this example, ``/mnt/kernels`` is an nfs mount which houses the kernel-debuginfo
packages. ``/cores`` is where all processed cores are stored and ``/tmp`` is the
temporary storage for collecting the necessary data from the kernel-debuginfos.
A mail server is setup within the environment to email CAS results and this
optional directive is shown to reflect that. Finally, the CAS server is an x86_64
machine and the environment will be processing x86 cores, therefore, the directive
for this is uncommented and path to the x86 crash binary is given. ``Note`` there
is information provided within the configuration file for installing the x86 crash
to a different location.

Altering the configuration to reflect the above assumptions would show the
following::

    [settings]
    casuser=cas
    kernels=/mnt/kernels
    rpmFilter=.*kerne.+-debuginfo-[0-9].*\.rpm
    debugs=/tmp
    debugLevel=DEBUG
    workDirectory=/cores
    smtphost=mail.cas-server.com
    database=/var/db/cas/cas.db
    [maintenance]
    purgeLimit=90
    autoPurge=Yes
    [advanced]
    crash_32=/usr/local/i386/crash
    #buffer=None

Now that the configuration file is altered and ``/mnt/kernels`` should be populated
with kernel-debuginfo rpm's the next section will describe running CAS.

Running CAS
^^^^^^^^^^^

First, one or two administrative tasks need to be run. The required task is to build
a database for all the data gathered from the kernel-debuginfo packages.::

    $ cas-admin -b

If several systems are deployed for CAS to use, ssh keys must be setup between the host (CAS) and
the clients::

    (cas-server) $ ssh-keygen -t dsa
    Cas supports passwordless entries at this time.
    (cas-server) $ ssh-copy-id -i ~/.ssh/id_dsa casuser@cas-client-system.com

Once ssh has been setup between systems the following will build the server database::

    $ cas-admin -s

Please note that in order for cas to function properly it is required that only the cas
user on the system has only those entries in its ssh hostkey file that are accessible
with cas. Cas will error with ``Authentication Failed`` and exit cleanly if it runs
into any system that it can not communicate with.

At this point CAS is configured and looking at the output of CAS help there are 
a few options to pass::

    Usage: cas [opts] args

    Options:
      -h, --help            show this help message and exit
      -i IDENTIFIER, --identifier=IDENTIFIER
                            Unique ID for core
      -f FILENAME, --file=FILENAME
                            Filename
      -e EMAIL, --email=EMAIL
                            Define email for results (must be valid!)
      -m, --modules         Extract associated kernel modules

CAS prepares its directory hierarchy based on the ``identifier`` this option is
therefore required. ``filename`` is also required as it tells CAS exactly which
core to process and associate with ``identifier``. If wanting email results from
CAS simply pass it the email parameter.

An example, of a user wanting to process a corefile named ``vmcore.12345``::

    $ cas -i 12345 -f vmcore.12345 -e user@cas-server.com

In the above example an assumption is made that ``1`` is associated to some
form of ticketing system so to keep things organized an identifier was set of
that number.

The directory hierarchy for the current job should look like ``/cores/1``.
In addition to the processing of core files there is also a ``process log`` contained
within this directory for each job processed. If multiple jobs for the same identifier
are issued they are placed within a sub directory marked by the current timestamp
and the relevant data associated with it.

The last option worth mentioning is for core analyst who are needing to work
within the core that requires one of the kernel modules loaded during the crash.
This can be extracted by passing the ``modules`` parameter in the CAS execution
statement. ``Note`` the ``modules`` parameter is not heavily used but can be
useful when analyzing filesystem issues and the like.

From this point on CAS  will download, process, and email the results of its
initial analysis to the specified email address. From there further instructions
are provided in either the email or the ``process log`` on how to access and analyze
the core.

Analyzing
---------

Continuing with the previous example the results of CAS processing should be emailed
and look something similar to::

    Subject: CAS results for 1
    Date: Tue, 06 May 2009 08:41:20 -0500
    
    Location: Location: /cores/1/2009.05.06.08.41.20
    Server: x86_64.cas-server.com
    Output data:
    PID: 0      TASK: ffffffff803e9b80  CPU: 0   COMMAND: "swapper"
     #0 [ffffffff8047a0a0] smp_call_function_interrupt at ffffffff8011d191
     #1 [ffffffff8047a0b0] call_function_interrupt at ffffffff80110bf5
    --- <IRQ stack> ---
     #2 [ffffffff80529f08] call_function_interrupt at ffffffff80110bf5
        [exception RIP: default_idle+32]
        RIP: ffffffff8010e7a9  RSP: ffffffff80529fb8  RFLAGS: 00000246
        RAX: 0000000000000000  RBX: 0000000000000000  RCX: 0000000000000018
        RDX: ffffffff8010e789  RSI: ffffffff803e9b80  RDI: 0000010008001780
        RBP: 0000000000000000   R8: ffffffff80528000   R9: 0000000000000080
        R10: 0000000000000100  R11: 0000000000000004  R12: 0000000000000000
        R13: 0000000000000000  R14: 0000000000000000  R15: 0000000000000000
        ORIG_RAX: fffffffffffffffa  CS: 0010  SS: 0018
     #3 [ffffffff80529fb8] cpu_idle at ffffffff8010e81c
    
    PID: 0      TASK: 100f57cb030       CPU: 1   COMMAND: "swapper"
     #0 [1000107bfa0] smp_call_function_interrupt at ffffffff8011d191
     #1 [1000107bfb0] call_function_interrupt at ffffffff80110bf5
    --- <IRQ stack> ---
     #2 [10001073e98] call_function_interrupt at ffffffff80110bf5
        [exception RIP: default_idle+32]
        RIP: ffffffff8010e7a9  RSP: 0000010001073f48  RFLAGS: 00000246
        RAX: 0000000000000000  RBX: 0000000000000e86  RCX: 0000000000000018
        RDX: ffffffff8010e789  RSI: 00000100f57cb030  RDI: 00000102000a4780
        RBP: 0000000000000001   R8: 0000010001072000   R9: 0000000000000040
        R10: 0000000000000000  R11: 0000000000000008  R12: 0000000000000000
        R13: 0000000000000000  R14: 0000000000000000  R15: 0000000000000000
        ORIG_RAX: fffffffffffffffa  CS: 0010  SS: 0018
     #3 [10001073f48] cpu_idle at ffffffff8010e81c
    
    PID: 6122   TASK: 101f3658030       CPU: 2   COMMAND: "gfs_quotad"
     #0 [101f21efb20] start_disk_dump at ffffffffa03183ff
     #1 [101f21efb50] try_crashdump at ffffffff8014cc1d
     #2 [101f21efb60] die at ffffffff80111c90
     #3 [101f21efb80] do_invalid_op at ffffffff80112058
     #4 [101f21efc40] error_exit at ffffffff80110e1d
        [exception RIP: do_dlm_lock+366]

    ... snip ...

From this email a ``location`` is provided ``Location: /cores/1/2009.05.06.08.41.20``
and the server in which further analyzation can be continued ``x86_64.cas-server.com``.

Normally from a support perspective this email should contain enough information
for a kernel engineer to begin debugging the problem. Assuming more is needed
the information provided previously will prove beneficial for anyone wishing
to access this data.

Logging into the stated server and changing into the directory defined several
files are presented::

    $ pwd
    Location: /cores/1/2009.05.06.08.41.20 
    $ ls
    1.log  crash  crash.in  crash.out  usr  vmcore.12345 log memory modules sys traceback

``1.log``: contains any informational messages presented during the processing
of the core. Everything from informational to debug statements are provided here.

``crash``: a script autogenerated to provide an automated way of gathering intial
data from the coredump. ``Note`` if wanting to use this crash wrapper in a more
manual approach some alterations to the script need to occur.

crash wrapper in its original form::

    #!/bin/sh
      /usr/bin/crash \
        /cores/1/2009.05.06.08.41.20/vmcore.12345 \
          usr/*/*/*/*/2.6.9*largesmp/vmlinux $*

``Note`` Running the crash wrapper manually will result in an interactive instance.

**Alternative to using the crash wrapper**

It is possible to specify the vmlinux and corefile with crash on the command line::

    $ crash /cores/1/2009.05.06.08.41.20/usr/*/*/*/*/2.6.9*largesmp/vmlinux  \
        /cores/1/2009.05.06.08.41.20/vmcore.12345

``crash.in``: a list of commands to be read into crash during the automated
analysis::

    bt >> traceback
    bt -a >> traceback
    sys >> sys
    sys -c >> sys
    log >> log
    mod >> modules
    kmem >> memory
    kmem -f >> memory
    exit
    
This can be extended by adding more snippets into ``/var/lib/cas/snippets``. Please see
that directory for examples.

``crash.out``: output of initial crash analysis and the same data which
is sent in an email if defined.

``usr``: directory structure from the extraction of the vmlinux file
from the associated kernel-debuginfo rpm for use within crash::

    /cores/1/2009.05.06.08.41.20/
        usr/lib/debug/lib/modules/2.6.9-78.18.ELlargesmp/vmlinux

``vmcore.12345``: corefile from which was either defined or extracted from
a compressed archive during CAS initialization.

Troubleshooting
---------------

Some of the major problems that arise when using CAS usually boils down to some
improper usage of the compression and archiving tools.

When compressing a core which may need to be sent over the network to a CAS server
one of the proper ways to do so is::

    $ tar cvjf vmcore.12345.tar.bz2 vmcore.12345

Other various ways of compressing archive are as follows::

    $ tar cvzf vmcore.tar.gz vmcore 
    $ gzip vmcore 
    $ bzip2 vmcore 

``Note``: please do not double compress or CAS will fail.

Another issue, which isn't primarily a fault of CAS, are
incomplete or corrupted cores. If either of these occur
there is a chance that CAS will not be able to process
the data needed to associate a debug kernel or do any
sort of automated analysis. Unfortunately, there is not
much that can be done to resolve these sort of issues
other than verifying that the process which happens when
a system coredump and when that dump reaches the
system specified for retrieval is solid and are seeing
no errors.

Resources
=========

* `CAS Wiki <http://fedorahosted.org/cas>`_
* `CAS FAQ <https://fedorahosted.org/cas/wiki/CasFAQ>`_
* `Mailing list <https://fedorahosted.org/mailman/listinfo/cas>`_
* `Upstream releases <https://fedorahosted.org/releases/c/a/cas/>`_
* Checkout latest from Git, ``git clone git://git.fedorahosted.org/cas.git``

