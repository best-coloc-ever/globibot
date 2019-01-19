PERMISSION_NAMES = dict(
    create_instant_invite='Create instant invites',
    kick_members='Kick members',
    ban_members='Ban Members',
    administrator='Adminitrate stuff',
    manage_channels='Manage channels',
    manage_server='Manage the server',
    read_messages='Read messages',
    send_messages='Send messages',
    send_tts_messages='Send TTS messages',
    manage_messages='Manage messages',
    embed_links='Embed links',
    attach_files='Attach files',
    read_message_history='Read the message history',
    mention_everyone='Mention everyone',
    external_emojis='Use external emojis',
    connect='Connect to the voice channel',
    speak='Speak',
    mute_members='Mute members',
    deafen_members='Deafen members',
    move_members='Move members',
    use_voice_activation='Use voice activation',
    change_nickname='Change my nickname',
    manage_nicknames='Manage nicknames',
    manage_roles='Manage roles',
)

def permission_names(permissions):
    names = set()

    for attr, name in PERMISSION_NAMES.items():
        has_perm = getattr(permissions, attr)
        if has_perm:
            names.add(name)

    return names
