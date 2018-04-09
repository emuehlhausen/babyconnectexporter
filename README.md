# babyconnectexporter

This is a simple python 2 script that exports data from Baby Connect (https://www.baby-connect.com). You run the script, supply your credentials on the command line, and it will do the rest. The script produces one CSV file per child, sorted by the Start Time column.

Disclaimers:
There is no official API, I just reverse-engineered their existing export mechanism. The procedure used by this script could be easily broken by trivial site changes. The script has not been tested widely (I've only tried my own account, only on linux, etc.), so use at your own risk.

I have no connection to Baby Connect and they have no knowledge of my work. I have used their service and was frustrated to find that there's no simple export option, so I wrote this on my own, and thought it might be useful to others.
