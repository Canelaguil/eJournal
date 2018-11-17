
def in_response(response, *args):
    """Check if all the arguments are also in the response."""
    return {obj.pk for obj in args} <= {resp['id'] for resp in response}


def is_response(response, *args):
    """Check if all the arguments are also in the response and the other way around."""
    return {obj.pk for obj in args} == {resp['id'] for resp in response}
