from . import Function

environment_variable = Function('environment-variable')
available_environment_variables = Function('available-environment-variables')
unparsed_text_available = Function('unparsed-text-available', args_count=1)
unparsed_text = Function('unparsed-text', args_count=1)
unparsed_text_lines = Function('unparsed-text-lines', args_count=1)
generate_id = Function('generate-id', args_count=1)
