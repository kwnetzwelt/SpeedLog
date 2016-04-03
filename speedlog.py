#!/usr/bin/env python

__title__ = "SpeedLog"
__description__ = "Runs speedtest-cli and stores the result in a file including a timestamp for parsing. "
__author__ = "Kai Wegner"
__copyright__ = "Copyright 2016, Kai Wegner"
__license__ = "MIT"
__version__ = "0.0.1"


from subprocess import Popen, PIPE
import logging
import string
import sys
import getopt
import datetime
import os
import stat


logging.basicConfig(filename='speedtest.log',level=logging.DEBUG, format='%(asctime)s %(message)s')

def parse_output(output):
    outputLines = output.splitlines(True)
    
    d = filter(lambda l: l.startswith("Download:"), outputLines)
    d = d[0][10:].split(" ")

    u = filter(lambda l:l.startswith("Upload: "), outputLines)

    u = u[0][8:].split(" ")

    return (u[0], u[1], d[0], d[1])

def run_speed_test(pretend):
    logging.info("running speedtest")

    if not pretend:
        process = Popen(["speedtest-cli"], stdout=PIPE)
        (output, err) = process.communicate()
        exit_code = process.wait()
    else:
        exit_code = 0
        output = """Retrieving speedtest.net configuration...
Retrieving speedtest.net server list...
Testing from Tele Columbus AG (5.28.97.87)...
Selecting best server based on latency...
Hosted by SysEleven GmbH (Berlin) [14.47 km]: 23.58 ms
Testing download speed........................................
Download: 7.36 Mbit/s
Testing upload speed..................................................
Upload: 1.25 Mbit/s"""

    if exit_code == 0:
        logging.info("speed test successful")
    else:
        logging.error("error running speedtest")
        logging.error("error was" + err)
        raise Exception("speed test failed")
    
    return output
    return parse_output(output)



class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hv", ["help","version"])
        except getopt.error, msg:
            raise Usage(msg)
        if len(args) > 0:
            __outputfile__ = args[0]
        else:
            __outputfile__ = "output.txt"
        for o, a in opts:
            if o in ("-h", "--help"):
                print ""
                print "\t" + __title__
                print ""
                print "\t" + __description__ + " by " + __author__
                print ""
                print "\t-v --version     prints version information"
                print "\t-h --help        prints this help display and exits"
                print ""
            elif o in ("-v", "--version"):
                print __title__ + ": " +  __version__
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2
    try:    
        if not os.path.isfile(__outputfile__):
            file(__outputfile__, "w").close()


        testresult = run_speed_test(pretend=False)
        (up, upunit, down, downunit) = parse_output(testresult)

        date = datetime.datetime.now().isoformat()
        output = [date.strip(), up.strip(), upunit.strip(), down.strip(), downunit.strip()]
        output = ";".join(output)
        logging.info(output)

        with open(__outputfile__,"ab") as outfile:
            outfile.write(output + "\n")
    except Exception as exc:
        print>>sys.stderr, exc

if __name__ == "__main__":
    sys.exit(main())
