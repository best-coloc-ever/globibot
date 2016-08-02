COMMAND_VALIDATORS_ATTR = 'validators'

NO_HOOK = lambda bot, message: True

def validator(validate, pre_hook=NO_HOOK, **kwargs):

    def wrapped(func):

        def call(plugin, message, *args, **kwargs):
            if pre_hook(plugin.bot, message):
                return func(plugin, message, *args, **kwargs)

        if hasattr(func, COMMAND_VALIDATORS_ATTR):
            validators = getattr(func, COMMAND_VALIDATORS_ATTR)
            validators.append(validate)
            setattr(call, COMMAND_VALIDATORS_ATTR, validators)
        else:
            setattr(call, COMMAND_VALIDATORS_ATTR, [validate])

        return call

    # For introspection
    validate.pre_hook = pre_hook

    return wrapped
