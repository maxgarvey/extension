extension
=========

this is the sponsored account extender webapp.

Currently, it is not functional, because the correct permissions to modify the psuAccountExpireDate field are TBD. Also, since it hasn't been deployed on production, the file permissions are likely incorrect. Also, django-admin hasn't been set up. This stuff is fairly easy to change though. I will attempt to code up and comment out as much of this type of stuff as I can prior to my departure.

TODO:
  Setup django-admin: uncomment lines in /settings.py as well as /urls.py. uncomment login required wrappers in /views.py
  Uncomment section modifying the psuAccountExpireDate field.
  Modify conf.py to reflect the new service account credentials with correct permissions.
  Possibly add section to renew expired account?
  When actually deployed, will have to add privileges to users via command line prior to being able to do it through the gui at <url>/admin
  Setting up apache and DNS to support the new app.
