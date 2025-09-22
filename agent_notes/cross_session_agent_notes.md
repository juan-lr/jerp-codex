# Meta Info
- Some items in README.md files are not yet implemented check for yourself
- This is a mostly a "playground" for AI agents. The real codebase uses
Docker-orchestrated containers for the database and the lerp submodule. Since
you don't have access to docker, for integration tests, install postgis directly
and the djangp project directly in your environment when you are prompoted to
run integration tests

- Anything and everything not listed under set-in-stone is editable
- What is set-in-stone:
    - PostGIS as the primary database
    - django as the logic backend

# More Project descriptions
- Farm planning is built from nested containers: OrgPlan
(future) or RanchPlan at the top, then FieldPlan, then
FieldActivity, down to FieldActivityElement. Crop templates
mirror that hierarchy (CropPlan → CropPlanFieldActivity →
CropPlanFieldActivityElement) and instantiate concrete field
plans. Budgets live in templates (per-acre), while executing/
closing a field activity turns that stack into the “actual,”
with version history preserved for comparisons.
- Desired permissions piggyback on that container stack.
Roles are defined inside each organization; a role is just
a bundle of object-level permissions scoped to specific
plan containers. Whoever holds the role on, say, a RanchPlan
automatically gains inherited access down to every FieldPlan,
FieldActivity, and FieldActivityElement inside that ranch.
“Template” objects follow the same idea: grant on a CropPlan
lets you view/copy/create its CropPlanFieldActivity children;
instantiating a field plan from the template requires the
appropriate create permission at the destination container.
- Extra permission flags (e.g., view_financials) further
constrain sensitive fields. If a role lacks view_financials,
the user may still arrange schedules or mark activities
complete but can’t see or edit the cost/price attributes
attached to those elements—even though they can reach the
container.
- Practically, the first admin of each organization seeds
the role assignments, after which admins can delegate:
e.g., planning_manager (full CRUD on Ranch/Field plans),
field_foreman (view + mark activities actual), agronomist
(read templates, propose edits) while accounting-only roles
skip view_financials.
- Net result: planning data stays hierarchical and versioned,
templates remain reusable, and permissions flow from the
organizational container model so that budget-vs-actual
tracking can involve operations staff without leaking
financial-sensitive data.
