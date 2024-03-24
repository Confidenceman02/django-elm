"""
djelm expects the MainFlags variable to be present
when running 'manage.py djelm generatemodel <app-name>'.

For the best developer experience, Make sure you don't rename the variable or
change the return type to anything that isn't a valid Flag.
"""

from djelm.flags import Flags, IntFlag

MainFlags = Flags(IntFlag())
