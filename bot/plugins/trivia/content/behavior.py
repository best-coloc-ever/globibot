def trivia_behavior(fetch, pick, premise, query, resolve):

    def init():
        dataset = fetch()
        p = pick(dataset)

        def behavior():
            item = p()
            yield premise(item)
            answers = yield query
            yield resolve(item, answers)

        return behavior

    return init
