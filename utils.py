from pwdlib import PasswordHash

pass_hash = PasswordHash.recommended()


def hashPassword(password: str):
    return pass_hash.hash(password)


def verifyPassword(password: str, hashed_pass: str):
    return pass_hash.verify(password, hashed_pass)
