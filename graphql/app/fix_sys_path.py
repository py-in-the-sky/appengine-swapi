"""
This is used for test setup only.

GAE path setup borrowed from:
https://cloud.google.com/appengine/docs/python/tools
/localunittesting#Python_Setting_up_a_testing_framework

After this script runs, all `google.appengine.*` packages
are available for import, as well as all GAE-bundled third-party
packages.
"""


from os.path import expanduser
from sys import path


gae_sdk_path = expanduser('~/google-cloud-sdk/platform/google_appengine')


if gae_sdk_path not in path:
    path.insert(0, gae_sdk_path)


import dev_appserver


dev_appserver.fix_sys_path()
