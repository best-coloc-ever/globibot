# from globibot.lib.helpers import formatting as f

from tornado.httpclient import AsyncHTTPClient
from tornado.platform.asyncio import to_asyncio_future

from asyncio import sleep, wait
from time import time as now

import os.path
import random
import json

class Utils:

    async def fetch(url):
        client = AsyncHTTPClient()
        tornado_future = client.fetch(url)
        future = to_asyncio_future(tornado_future)
        response = await future

        return response.body

class Fetch:

    DATA_FILE = lambda name: os.path.join('./plugins/trivia/data', name)

    def read_json(file_name):

        def reader():
            with open(Fetch.DATA_FILE(file_name), 'r') as f:
                return json.load(f)

        return reader

class Pick:

    def random_collection(dataset):
        random.shuffle(dataset)
        index = 0

        def pick():
            nonlocal index
            item = dataset[index]
            index += 1
            if index >= len(dataset):
                index = 0
                random.shuffle(dataset)
            return item

        return pick

    def random_dict_item(dataset):
        return Pick.random_collection(list(dataset.items()))

class Query:

    def timed(delay):

        # async def query(read_message):
        #     messages = []
        #     answered = set()
        #     start = now()

        #     while True:
        #         timeout = delay - (now() - start)

        #         if timeout <= 0:
        #             return messages

        #         message_set, _ = await wait((read_message(), ), timeout=timeout)

        #         try:
        #             message_task = next(iter(message_set))
        #             message = message_task.result()
        #         except StopIteration:
        #             pass
        #         else:
        #             if message.author.id not in answered:
        #                 messages.append(message)
        #                 answered.add(message.author.id)

        async def query():
            await sleep(delay)

        return query

def readable_concat(collection):
    comma_string = ', '.join(collection[:-1])
    return ' and '.join(e for e in (comma_string, collection[-1]) if e)

def time_diff(delta):
    return delta.seconds + (delta.microseconds / 1000000)

class Resolve:

    def fastest(answers, to_find, skill):
        winning_answers = [
            answer for answer in answers
            if answer.clean_content.strip().lower() == to_find
        ]

        if not winning_answers:
            return None, 'Nobody found in time, the answer was: `{}`'.format(to_find)
        else:
            fastest_answer, *other_answers = winning_answers

            winners_mention = readable_concat([
                answer.author.mention
                for answer in winning_answers
            ])
            message = (
                '{} found the correct answer! It was: `{}`'
                    .format(winners_mention, to_find)
            )

            if other_answers:
                other_times = ' - '.join(
                    '{} `+{:.3f}`'.format(
                        answer.author.mention,
                        time_diff(answer.timestamp - fastest_answer.timestamp)
                    )
                    for answer in other_answers
                )
                detail = (
                    '{} was the fastest to answer though\n{}'
                        .format(fastest_answer.author.mention, other_times)
                )
                message += '\n{}'.format(detail)

            conclusion = (
                '{} killed everyone else with superior {} skills'
                    .format(fastest_answer.author.mention, skill)
            )

            return fastest_answer.author, '{}\n{}'.format(message, conclusion)

    def closest_int(answers, to_find, within, skill):
        def is_integral(s):
            try:
                int(s)
            except:
                return False
            else:
                return True

        valid_answers = [
            answer for answer in answers
            if is_integral(answer.clean_content.strip())
        ]

        try:
            closest_diff = min(
                abs(to_find - int(answer.clean_content.strip()))
                for answer in valid_answers
            )
            closest_diff = min(within, closest_diff)
        except ValueError:
            return None, 'Nobody found in time, the answer was: `{}`'.format(to_find)

        winning_answers = [
            answer for answer in valid_answers
            if abs(to_find - int(answer.clean_content.strip())) == closest_diff
        ]

        if not winning_answers:
            return None, 'Nobody found in time, the answer was: `{}`'.format(to_find)
        else:
            fastest_answer, *other_answers = winning_answers

            winners_mention = readable_concat([
                answer.author.mention
                for answer in winning_answers
            ])

            detail = (
                'found the correct answer'
                if closest_diff == 0
                else '{} close'.format('were' if other_answers else 'was')
            )
            message = (
                '{} {}! It was: `{}`'
                    .format(winners_mention, detail, to_find)
            )

            if other_answers:
                other_times = ' - '.join(
                    '{} `+{:.3f}`'.format(
                        answer.author.mention,
                        time_diff(answer.timestamp - fastest_answer.timestamp)
                    )
                    for answer in other_answers
                )
                detail = (
                    '{} was the fastest to answer though\n{}'
                        .format(fastest_answer.author.mention, other_times)
                )
                message += '\n{}'.format(detail)

            conclusion = (
                '{} killed everyone else with superior {} skills'
                    .format(fastest_answer.author.mention, skill)
            )

            return fastest_answer.author, '{}\n{}'.format(message, conclusion)
