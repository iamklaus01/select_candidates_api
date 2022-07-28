class CustomError(Exception):
    pass

class EmailSyntaxeError(CustomError):
    """A specific error"""
    pass


def process():
    raise EmailSyntaxeError("L'adresse email est invalide!")

def caller():
    try:
        process()
    except Exception:
        pass