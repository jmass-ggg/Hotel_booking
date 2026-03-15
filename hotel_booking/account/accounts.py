def get_role_name(user):
    return getattr(getattr(user, "role", None), "name", None)


def get_actor_seller_profile(user):
    role_name = get_role_name(user)

    if role_name == "SELLER":
        return getattr(user, "seller_profile", None)

    if role_name == "SELLER_STAFF":
        staff_profile = getattr(user, "seller_staff_profile", None)
        if staff_profile:
            return staff_profile.seller

    return None