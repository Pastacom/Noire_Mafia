from Roles.Role import Role


class Civilian(Role):
    team = Role.RoleTeam.RED
    name = "Мирный житель"
    description = "Вы играете за красных. Ваша задача состоит в том, чтобы вычислить представителей мафии" \
                  " и посадить в тюрьму." \
                  " Сделать это вы можете только на дневном голосовании."
    image = "Data/civilian.jpg"
    multiplier = 1.4