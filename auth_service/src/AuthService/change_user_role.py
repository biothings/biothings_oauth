import sys

from auth.models import User, UserRole
from AuthService.database import Session


DB = Session()


def change_user_role(user_id, new_role):
    """
    Changes a user's role.

    @param user_id: ID of the user.
    @param new_role: The new role to set for the user.
    """

    roles = [r.name for r in UserRole]
    if new_role.upper() not in roles:
        raise Exception(f"The given role '{new_role}' is not valid!\n"
                        f"The available roles are: {', '.join(roles)}.")

    user = DB.query(User).filter(User.id == user_id).first()

    if not user:
        raise Exception(f"User with ID = {user_id} was not found!")

    user.role = new_role.upper()
    DB.commit()

    print(f"User with ID = {user_id} is now '{new_role.upper()}'.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise Exception("Bad script usage!\n"
                        "You must provide user ID with new user role.")

    change_user_role(int(sys.argv[1]), sys.argv[2])
