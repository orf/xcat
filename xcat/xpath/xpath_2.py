from . import Function

lower_case = Function("lower-case")
ends_with = Function('ends-with', args_count=2)
string_to_codepoints = Function("string-to-codepoints", args_count=1)
normalize_unicode = Function("normalize-unicode", min_args=1)
document_uri = Function("document-uri", min_args=0, max_args=1)
doc = Function("doc", args_count=1)
doc_available = Function("doc-available", args_count=1)
encode_for_uri = Function("encode-for-uri", args_count=1)
processing_instruction = Function('processing-instruction')
exists = Function('exists', args_count=1)
current_date_time = Function('current-dateTime')
resolve_uri = Function('resolve-uri', args_count=2)
