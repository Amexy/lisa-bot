from typing import Any


class Result:
    # here is where i'd use genrics but good luck with that in python right
    # "Any" it is
    success: Any
    failure: str

    def __init__(self, success: any = None, failure: str = None):
        self.success = success
        self.failure = failure


def createSuccess(success: any) -> Result:
    return Result(success=success)


def createFailure(failure: str) -> Result:
    print("creating {}".format(failure))
    return Result(failure=failure)
