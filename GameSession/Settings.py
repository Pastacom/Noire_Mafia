class Settings:
    game_mode_auto = True
    mutes = True
    hide = True
    time_limits = {"day speech": 60, "justification speech": 45, "vote": 15,
                   "condemned speech": 60, "single role": 40, "team role": 90}

    role_seed = {"civilian": True, "mafia": True, "don": True, "commissioner": True,
                 "doctor": False, "maniac": False, "courtesan": False, "immortal": False,
                 "two-face": False, "thief": False, "sergeant": False, "shapeshifter": False}

    role_quantity = {"civilian": 0, "mafia": 0, "don": 0, "commissioner": 0,
                     "doctor": 0, "maniac": 0, "courtesan": 0, "immortal": 0,
                     "two-face": 0, "thief": 0, "sergeant": 0, "shapeshifter": 0}
