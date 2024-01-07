## Installation
- Activate virtualenv
- Install all python requirements by `pip install -r requirements.txt`
- Execute `python -m uvicorn src.main:app --host 0.0.0.0 --reload` to run web service.
- All configuration variables are available in the config file in database folder.(You must set 
- `JWT_SECRET_KEY` and `JWT_REFRESH_SECRET_KEY`)

# All functions which have been performed in the system
- Add start service (to fetch and insert all memory information from the server) at the specific time interval.
- Add Authentication endpoints (user registration, login) based on jwt.
- Add role types (Admin, Regular) as authorization. (only Admin can start service `/start_service/)
- Add endpoint for fetching latest records from Memory models.
- Service startup solution is base on `from fastapi_utilities import repeat_every` and 
`from fastapi import BackgroundTasks`