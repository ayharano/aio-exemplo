#!/usr/bin/env python3
"""
asyncio working boilerplate for Python 3.5+.
"""

import asyncio
import sys


async def main(argv, *args, **kwargs):
    """Main function for asyncio's boilerplate example.

    Args:
        argv: variable size arguments.
        args: positional arguments.
        kwargs: keyword arguments.

    Returns:
        Implicit None.
    """

    return


if __name__ == '__main__':
    _LOOP = asyncio.get_event_loop()
    _LOOP.run_until_complete(main(sys.argv))
    # Wait for pending loop's tasks
    _PENDING = asyncio.Task.all_tasks()
    _LOOP.run_until_complete(asyncio.gather(*_PENDING))
    _LOOP.stop()
    _LOOP.close()
