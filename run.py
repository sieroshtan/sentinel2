import argparse
import jobrunner


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--farm_id', help='farm id from farm_boundaries table')
    parser.add_argument('-s', '--start', help='start date in ISO YYYY-mm-dd format')
    parser.add_argument('end', help='end date in ISO YYYY-mm-dd format')

    args = parser.parse_args()

    if args.start:
        jobrunner.run(args.farm_id, args.end, args.start)
    else:
        jobrunner.run(args.farm_id, args.end)

if __name__ == '__main__':
    main()
