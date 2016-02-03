allowed_match_methods = {"string", "code", "py"}


def make_matchmaker(match_input, match_method, is_true):
    if match_method == "string":
        def checker(response, body):
            return match_input in body
    elif match_method == "code":
        try:
            code = int(match_input)
        except ValueError:
            raise RuntimeError("Match method is status code but match input is not an integer")

        def checker(response, body):
            return response.status == code
    elif match_method == "py":
        raise NotImplementedError("ToDo :)")
    else:
        raise RuntimeError("Unknown match input: {input}".format(input=match_method))

    if not is_true:
        _old_checker = checker
        # Invert the match_method

        def checker(response, body):
            return not _old_checker(response, body)

    return checker
