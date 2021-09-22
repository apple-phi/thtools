# Overview of third party libraries included within ToeholdTools

ToeholdTools is licensed under the terms of the [GPLv3](https://github.com/lkn849/thtools/blob/master/LICENSE).

However, the distributed app is made using [PyInstaller](https://github.com/pyinstaller/pyinstaller).
This means that it includes a standalone copy of Python 3.8.11 and that all Python dependencies are bundled in as well.
The Python license is available [here](https://github.com/python/cpython/blob/main/LICENSE).

This is a compendium of projects which are packaged into the app,
generated by [pip-licenses](https://github.com/raimon49/pip-licenses) via our script [THIRD_PARTY_LICENSES.sh](https://github.com/lkn849/thtools/blob/master/THIRD_PARTY_LICENSES.sh).

To access this table from inside the app, click the button labelled `Legal` in the top right hand corner.

## Libraries included
| Name             | Version   | License                                                | URL                                              |
|------------------|-----------|--------------------------------------------------------|--------------------------------------------------|
| Eel              | 0.14.0    | MIT License                                            | https://github.com/samuelhwilliams/Eel           |
| Jinja2           | 3.0.1     | BSD License                                            | https://palletsprojects.com/p/jinja/             |
| MarkupSafe       | 2.0.1     | BSD License                                            | https://palletsprojects.com/p/markupsafe/        |
| bottle           | 0.12.19   | MIT License                                            | http://bottlepy.org/                             |
| bottle-websocket | 0.2.9     | MIT License                                            | https://github.com/zeekay/bottle-websocket       |
| dill             | 0.3.4     | BSD License                                            | https://github.com/uqfoundation/dill             |
| future           | 0.18.2    | MIT License                                            | https://python-future.org                        |
| gevent           | 21.8.0    | MIT License                                            | http://www.gevent.org/                           |
| gevent-websocket | 0.10.1    | Copyright 2011-2017 Jeffrey Gelens <jeffrey@noppo.pro> | https://www.gitlab.com/noppo/gevent-websocket    |
| greenlet         | 1.1.1     | MIT License                                            | https://greenlet.readthedocs.io/                 |
| multiprocess     | 0.70.12.2 | BSD License                                            | https://github.com/uqfoundation/multiprocess     |
| numpy            | 1.21.2    | BSD License                                            | https://www.numpy.org                            |
| nupack           | 4.0.0.23  | UNKNOWN                                                | www.nupack.org                                   |
| pandas           | 1.3.3     | BSD License                                            | https://pandas.pydata.org                        |
| pathos           | 0.2.8     | BSD License                                            | https://github.com/uqfoundation/pathos           |
| pox              | 0.3.0     | BSD License                                            | https://github.com/uqfoundation/pox              |
| ppft             | 1.6.6.4   | BSD-like                                               | https://github.com/uqfoundation/ppft             |
| prettytable      | 2.2.0     | BSD License                                            | https://github.com/jazzband/prettytable          |
| psutil           | 5.8.0     | BSD License                                            | https://github.com/giampaolo/psutil              |
| pyparsing        | 2.4.7     | MIT License                                            | https://github.com/pyparsing/pyparsing/          |
| python-dateutil  | 2.8.2     | Apache Software License; BSD License                   | https://github.com/dateutil/dateutil             |
| pytz             | 2021.1    | MIT License                                            | http://pythonhosted.org/pytz                     |
| scipy            | 1.7.1     | BSD License                                            | https://www.scipy.org                            |
| setuptools       | 56.0.0    | MIT License                                            | https://github.com/pypa/setuptools               |
| six              | 1.16.0    | MIT License                                            | https://github.com/benjaminp/six                 |
| wcwidth          | 0.2.5     | MIT License                                            | https://github.com/jquast/wcwidth                |
| whichcraft       | 0.6.1     | BSD License                                            | https://github.com/pydanny/whichcraft            |
| zope.event       | 4.5.0     | Zope Public License                                    | https://github.com/zopefoundation/zope.event     |
| zope.interface   | 5.4.0     | Zope Public License                                    | https://github.com/zopefoundation/zope.interface |