from slowapi import Limiter
from slowapi.util import get_remote_address

# In-memory limiter keyed by client IP. Good enough for a single backend
# process; if the app is ever scaled to multiple instances, swap the storage
# for Redis (slowapi supports it via `storage_uri`) so limits are shared.
limiter = Limiter(key_func=get_remote_address)
