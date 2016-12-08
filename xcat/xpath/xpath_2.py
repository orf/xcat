from . import Function

lower_case = Function("lower-case")
string_to_codepoints = Function("string-to-codepoints", args_count=1)
normalize_unicode = Function("normalize-unicode", args_count=1)
document_uri = Function("document-uri", args_count=1)
doc = Function("doc", args_count=1)
encode_for_uri = Function("encode-for-uri", args_count=1)
processing_instruction = Function('processing-instruction')
