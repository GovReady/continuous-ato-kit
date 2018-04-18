#!/usr/bin/env python3.6

import os.path
import time
import json

# wait for Q to finish initializing
while not os.path.exists("/tmp/govready-q-is-ready"):
	print("Waiting for GovReady-Q to start up...")
	time.sleep(4)

# initialize django
import os; os.environ.setdefault("DJANGO_SETTINGS_MODULE", "siteapp.settings")
import django; django.setup()

from siteapp.models import User, Organization, Folder
from guidedmodules.models import AppSource, TaskAnswer
from siteapp.views import start_app

# Set up a User named "demo" and print its API key.
###################################################
print("Creating administrative user...")
user, is_new = User.objects.get_or_create(username='demo', is_superuser=True, is_staff=True)
password = User.objects.make_random_password(length=24)
user.set_password(password)
user.save()
print("Username:", user.username)
print("Password:", password)
print("API Key:", user.get_api_keys()['rw'])

# Set up a new Organization and make the user an admin of it.
#############################################################
print("Creating default organization...")
org = Organization.objects.filter(subdomain="main").first()
if not org:
  org = Organization.create(name='Dept of Sobriety', subdomain="main", admin_user=user)

# Fill in this user's account profile in this organization.
###########################################################
user_profile = user.get_settings_task(org)
user_profile_name, _ = TaskAnswer.objects.get_or_create(task=user_profile, question=user_profile.module.questions.get(key="name"))
user_profile_name.save_answer("Security Engineer", [], None, user, "web")

# Add an AppSource that holds the demonstration compliance apps.
################################################################
print("Adding TACR Demo Apps...")
appsrc, is_new = AppSource.objects.get_or_create(slug="demo")
appsrc.spec = { 'type': "git", "url": "https://github.com/GovReady/tacr-demo-apps" }
appsrc.save()

# Start the top-level app.
##########################
print("Starting compliance app...")
folder = Folder.objects.create(organization=org, title="Target App")
top_project = start_app(appsrc.slug + "/tacr_main_app", org, user, folder, None, None)

# Start the inner app.
######################
task = top_project.root_task
q = task.module.questions.get(key="file_server")
inner_project = start_app(appsrc.slug + "/unix_file_server", org, user, None, task, q)
print("API URL:", inner_project.get_api_url())
