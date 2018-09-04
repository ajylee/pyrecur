#  Copyright 2018 Andrew Lee
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


"""
===============================
Optimized recursion techniques
===============================

See `Examples and Testing` at the bottom for usage examples.
"""

import logging


# Logging facilities
# -------------------

logger = logging.getLogger(__name__)


def trace_id(label, x):
    if logger.level <= logging.DEBUG:
        if label:
            logger.debug('{}: {}'.format(label, x))
        else:
            logger.debug(x)

    return x


# Wrappers
# ---------

class Call:
    """Reifies a function call"""
    def __init__(self, fn, *args, **kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        
    def once(self):
        return self.fn(*self.args, **self.kwargs)
    

class Yielder(Call):
    """Reifies a call that returns an iterator"""
    def __iter__(self):
        yield from self.once()
    

# Recursion handlers
# -------------------

def recur(maybe_call):
    """Recursively calls a `Call`.

    Recursive calls are wrapped in `Call`.
    Supports tail recursive call optimization.
    Only supports tail recursive calls.

    """
    while isinstance(maybe_call, Call):
        maybe_call = maybe_call.once()

    return maybe_call

    
def recur_gen(maybe_yielder):
    """Recursively yields from iterators.

    Yielders are treated as recursive calls that return iterators.
    Supports tail call optimization.
    Only supports tail recursive calls.

    """
    while True:
        for elt in maybe_yielder:
            if isinstance(elt, Yielder):
                maybe_yielder = elt
                break  # go to top of while
            else:
                yield elt
        else:
            # less confusing than break
            return    

        

# Examples and testing
# ---------------------

# Test recur_gen
def all_substrings(s):
    if 1 < len(s):
        for ii in trace_id('', range(1, len(s))):
            yield trace_id('', s[0:ii])
        yield trace_id('', s[1:])
        yield Yielder(all_substrings, s[1:])


def test_all_substrings():
    assert set(recur_gen(all_substrings('abcd'))) == {
        'a', 'b', 'c', 'd', 'ab', 'bc', 'cd', 'abc', 'bcd'
    }


# Test recur
def build_cycle(ll, cycle):
    _next = ll[cycle[-1]]
    if _next == cycle[0]:
        return cycle
    else:
        cycle.append(_next)
        return Call(build_cycle, ll, cycle)

    
def regular_build_cycle(ll, cycle):
    _next = ll[cycle[-1]]
    if _next == cycle[0]:
        return cycle
    else:
        cycle.append(_next)
        return regular_build_cycle(ll, cycle)


def test_build_cycle():
    ll = [0, 3, 4, 2, 5, 1]
    assert recur(build_cycle(ll, [1])) == [1, 3, 2, 4, 5] == regular_build_cycle(ll, [1])


if __name__ == '__main__':
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    test_all_substrings()
    test_build_cycle()
