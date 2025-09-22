# lerp
A Django backend for an Enterprise Resource Planning (ERP) program

This project is meant to track resources and facilitate collaboration within and
accross organizations. Each organization will have multiple users, and users can
be a part of multiple organizations with different roles in each. Actions and
environments will be limited so that there is always a clear
organization-context for users.

## Measurments and Database (PostGis)
- Database is declared in jerp compose files - does not have its own submodule
- db image: postgis/postgis:17-3.5
- SRID 4326 used everywhere
- Within the backend and DB, all quantities must be in SI units
    - Instead of storing units, we store physical dimensions
    - Users may set their prefered units for input and reading, but input
    is immediatley converted to SI, and convertions happen after any
    calculations that must be done when reading

## Project Scale
The first organizations expected to use this project will be crop farms,
custom (outsourced) farming service providers, and labor contractors. During MVP
development, there may only be 10s of users and organizations, but there will be
a few big container objects each with up to thousands of objects to be managed
by those few users. A best-effort is made to build this project with growth
in mind.

## Permissions
A role is a set of permissions within an organizations. All organizations will
have at least one user with and admin role to manage everything within their
organization. This is not a unique organization owner. The first admin can
create others.

Object-level permissions are supported for some models, mostly those that act as
containers. Permission will extend to any objects within a containter.
To further narrow permissions, we can specify a permission such as
`view_financials` so that if a user has access to a container, but does not have
the `view_financials` permissions, they will not be able to see objects or
attributes within said container marked as requiring that permission.

## Apps

### conf
The "project" containing settings.py

### core
Holds constructs central to all other apps. Noteable models include:
- Dimension: A TextChoices object for users to choose their method of measurment
- <Dimension>Unit: A set of objects for users to choose their units
- Organization
- OrgObject: A Mixin to give other models an organization FK

### users
- Creates custom User identical to auth.User for future extension needs
- May hold Profile model in future - depends on imports not becoming circular

### pages
- Exists to create seperation between user and important (core) apps for
security
- Will hold simple - low-interactivity pages like about.html
- May hold templates.views for other apps

### accounting
- Primarily holds accounting-code models for various entities
    - e.g. input-materials, products, etc.
- CashFlowItem for recording transactions
- Imports from core

### resources
- Holds operations-code models mirroring those in accounting
    - This allows accounting and operations departments to have their own codes
    - This is useful if accounting uses its own ERP and operations wants a
    different organizational structure
    - If an organization does not have this split nature, they need not set both
    types of codes
- Asset and Inventory models
- Imports from core

### equipment
- Holds non-consumable asset models such as Tractor and Implement
- Imports from core and resources

### realestate
- Holds Ranch, Field, etc. models

### farmplanning
- Brings everything together from other apps into planning-related models
- Imports from core, resources, equipment, realestate, and accounting
- See README.md in farmplanning folder
