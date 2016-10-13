COMMAND_VALIDATORS_ATTR = 'validators'

def validator(validate, *hooks, **kwargs):

    def wrapped(func):

        def call(plugin, message, *args, **kwargs):
            hook_results = [
                hook(plugin.bot, message)
                for hook in hooks
            ]
            if all(hook_results):
                return func(plugin, message, *args, **kwargs)

        if hasattr(func, COMMAND_VALIDATORS_ATTR):
            validators = getattr(func, COMMAND_VALIDATORS_ATTR)
            validators.append(validate)
            setattr(call, COMMAND_VALIDATORS_ATTR, validators)
        else:
            setattr(call, COMMAND_VALIDATORS_ATTR, [validate])

        return call

    # For introspection
    validate.hooks = hooks

    return wrapped
