import argparse

import jobrunner


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('end', help='end date in ISO YYYYmmdd format')
    parser.add_argument('-s', '--start', help='start date in ISO YYYYmmdd format')

    args = parser.parse_args()

    if args.start:
        jobrunner.run(date_from=args.start, date_to=args.end)
    else:
        jobrunner.run(date_to=args.end)

if __name__ == '__main__':
    main()
