COMMAND_VALIDATORS_ATTR = 'validators'

NO_HOOK = lambda bot, message: None

def validator(validate, pre_hook=NO_HOOK, **kwargs):

    def wrapped(func):

        def call(module, message, *args, **kwargs):
            pre_hook(module.bot, message)
            return func(module, message, *args, **kwargs)

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
