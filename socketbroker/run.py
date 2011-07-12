import logging
import argparse
from socketbroker import broker
from socketbroker import flashpolicy 
import sys 

def main():
    logger_levels = {
            'debug' : logging.DEBUG,
            'info'  : logging.INFO,
            'warn'  : logging.WARN}
    parser = argparse.ArgumentParser(description = "Adobe Flash Socket Message broker",
                                     epilog = "<c> SIA True-Vision http://www.true-vision.net/")
    parser.add_argument('--port', type = int, help="port to listen", default = 1001)
    parser.add_argument('--ip', type = str, help = "ip address to listen", default = "0.0.0.0")
    parser.add_argument('--verbose', type = str, help = "verbosity level", choices = logger_levels.keys(), default = 'warn')
    args = parser.parse_args()
    
    logging.basicConfig(level=logger_levels[args.verbose])
    logging.info('Creating host')
    logging.info("command line arguments: %s", args)
    try:
        try:
            broker_server = broker.start(args.ip, args.port)
        except:
            raise
            logging.critical("bind to %s:%d failed " % (args.ip, args.port))
            sys.exit(1)
        try:
            flashpolicy_server = flashpolicy.start(args.ip, dest_port = args.port)
        except:
            broker.shutdown()
            logging.critical("bind to %s:%d failed " % (args.ip, 743))
            sys.exit(1)
        while True: #ethernal loop
            pass
    except KeyboardInterrupt as error:
        logging.info("Got CTRL+C, shutting down gracefully")
        broker_server.shutdown()
        flashpolicy_server.shutdown()
        sys.exit(0)


if __name__ == '__main__':
    main()
