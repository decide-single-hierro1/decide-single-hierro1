#!/usr/bin/env python
import os
import sys
import threading
import asyncio


 

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "decide.settings")
    try:
	
        from django.core.management import execute_from_command_line
        from bot import bot

    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    
 
    
    threading.Thread(target = lambda:  bot.init()).start()
    threading.Thread(target= execute_from_command_line(sys.argv)).start()
    
    
    
   

    


