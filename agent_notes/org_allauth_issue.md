# Note on django-organizations
django-organizations docs are outdated in some areas but the project is clearly active - looks like a small community

If the issue below is a straight-forward fix - we can resolve it as a selfish requirment

# Open Issue 284

## user
Currently user_pk can only be int.

in Django-AllAuth, the User id is UUID, so got this error:

django.urls.exceptions.NoReverseMatch: Reverse for 'organization_user_detail' with keyword arguments '{'organization_pk': 1, 'user_pk': UUID('097bc703-ba00-4215-95ee-9dc1a397a52b')}' not found. 1 pattern(s) tried: ['organizations/(?P<organization_pk>[0-9]+)/people/(?P<user_pk>[0-9]+)/\\Z']

As an enhancement, can we add config (settings.py) option to support user_pk with UUID?

## maintainer
I'm on board with this. And to document a little more clearly, the improvement here would be to make the OrganizationUserBase foreign key to the auth.AUTH_USER_MODEL configurable or otherwise dynamic such that it uses the field type of the auth.AUTH_USER_MODEL primary key.
