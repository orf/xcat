from . import Function

current_dir = Function('Q{http://expath.org/ns/file}current-dir')
read_binary = Function('Q{http://expath.org/ns/file}read-binary', args_count=1)
write_binary = Function('Q{http://expath.org/ns/file}write-binary', args_count=2)
append_binary = Function('Q{http://expath.org/ns/file}append-binary', args_count=2)

read_text = Function('Q{http://expath.org/ns/file}read-text', args_count=1)
write_text = Function('Q{http://expath.org/ns/file}write-text', args_count=2)

base_64_binary = Function('xs:base64Binary', args_count=1)

delete = Function('Q{http://expath.org/ns/file}delete', args_count=1)
