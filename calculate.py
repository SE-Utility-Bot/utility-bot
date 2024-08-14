import sys
import urllib.request as u
import urllib.parse as p


print(u.urlopen(f"https://safe-exec.onrender.com/{p.quote(sys.argv[1], safe='')}").read().decode("utf-8"))
