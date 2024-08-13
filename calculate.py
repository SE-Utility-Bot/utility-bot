import sys
import urllib.request as u


print(u.urlopen(f"https://safe-exec.onrender.com/{sys.argv[1]}").read().decode("utf-8"))
