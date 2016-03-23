##from cx_Freeze import setup, Executable
##
### Dependencies are automatically detected, but it might need
### fine tuning.
##buildOptions = dict(packages = [], excludes = [])
##
##base = 'Console'
##
##executables = [
##    Executable('GUI.py', base=base, icon="MESA_favicon.ico")
##]
##
##setup(name='RSA5106B',
##      version = '0.4.1',
##      description = 'RSA5106B Control Software',
##      options = dict(build_exe = buildOptions),
##      executables = executables)


from distutils.core import setup
import py2exe

setup(console=['GUI.py'])
