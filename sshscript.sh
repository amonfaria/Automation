# get host key, if we know one
hostkeytype = None
hostkey = None
try:
host_keys = paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
except IOError:
try:
# try ~/ssh/ too, because windows can't have a folder named ~/.ssh/
host_keys = paramiko.util.load_host_keys(os.path.expanduser('~/ssh/known_hosts'))
except IOError:
print '*** Unable to open host keys file'
host_keys = {}

if host_keys.has_key(hostname):
hostkeytype = host_keys[hostname].keys()[0]
hostkey = host_keys[hostname][hostkeytype]
print 'Using host key of type %s' % hostkeytype

# now, connect and use paramiko Transport to negotiate SSH2 across the connection
try:
t = paramiko.Transport((hostname, port))
t.connect(username='user', password='pwd', hostkey=hostkey)
t.close()

except Exception, e:
print '*** Caught exception: %s: %s' % (e.__class__, e)
traceback.print_exc()
try:
t.close()
except:
pass
sys.exit(1)