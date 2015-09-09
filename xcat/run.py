from xcat import commands
import docopt


if __name__ == "__main__":
    arguments = docopt.docopt(commands.__doc__)

    try:
        run()
    except Exception as e:
        print("Error: {}".format(e))
        import sys

        sys.exit(-1)
