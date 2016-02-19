"""
I doubt that's the best way to do this, but this script allows me to debug the package without
building and installing it first. If I try to use the normal entry point ("__main__.py") the
absolute imports don't work (if package not installed) or use the old installed version of
the package
"""

from birdbody import __main__

if __name__ == "__main__":
	__main__.main()
