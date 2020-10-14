# External modules
import asyncio

# Internal modules
import ebay
import bot


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


def get_event_loop():
    return loop


def main():
    ebay.main()
    bot.main()


if __name__ == "__main__":
    main()
