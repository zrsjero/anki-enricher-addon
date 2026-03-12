from aqt import mw


def get_addon_config():
    return mw.addonManager.getConfig(__name__)


def get_note_type_name():
    config = get_addon_config()
    return config["note_type_name"]


def get_field_names():
    config = get_addon_config()
    return config["fields"]


def get_field_name(field_key):
    field_names = get_field_names()
    return field_names[field_key]


def get_example_count():
    config = get_addon_config()
    return config.get("example_count", 3)


def get_audio_prefix():
    config = get_addon_config()
    return config.get("audio_prefix", "jeeng")
