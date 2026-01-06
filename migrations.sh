uv run manage.py migrate --database=antragsmanagement antragsmanagement
uv run manage.py migrate --database=bemas bemas
uv run manage.py migrate --database=fmm fmm
uv run manage.py migrate --database=gdihrocodelists gdihrocodelists
uv run manage.py migrate --database=gdihrometadata gdihrometadata
uv run manage.py migrate
uv run manage.py antragsmanagement_roles_permissions
uv run manage.py bemas_roles_permissions
uv run manage.py fmm_roles_permissions
uv run manage.py gdihrocodelists_roles_permissions
uv run manage.py gdihrometadata_roles_permissions
uv run manage.py loaddata --database=gdihrometadata gdihrometadata_initial-data.json
