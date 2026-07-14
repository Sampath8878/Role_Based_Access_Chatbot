from dataclasses import dataclass


@dataclass
class UserContext:

    username: str

    role: str

    department: str

    is_admin: bool = False