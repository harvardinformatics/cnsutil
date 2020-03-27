# -*- coding: utf-8 -*-
'''
Calculate clean room time from door access

Created on  2020-03-27

@author: Aaron Kitzmiller <aaron_kitzmiller@harvard.edu>
@copyright: 2020 The Presidents and Fellows of Harvard College.
All rights reserved.
@license: GPL v2.0
'''

import MySQLdb
import sys
import os
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter

CLEAN_ROOM_ID = 24  # Room ID from NNIN database

def main(argv=None):
    '''
    Fetch room access data from cns_room_access_complete for a date range and create a table suitable for pivot.
    Separate InDirection and OutDirection rows are consolidated into a single row and written out
    with the time difference in seconds.

    New rows are started with each InDirection.  If there are multiple OutDirection records for the
    same person in the same day, the entire time is captured (the last OutDirection is recorded).

    When the day changes a new record is created.  In some cases, OutDirection records exist that do not have
    a corresponding InDirection (name or day has changed but an InDirection is not recorded first).
    These are reported with no value in the Time column, but the timestamp is recorded in the End column.
    '''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    SQL_DSN = {
        "host"      : os.environ.get("NNIN_HOSTNAME", "clean"),
        "db"        : os.environ.get("NNIN_DATABASE", "nnin"),
        "user"      : os.environ.get("NNIN_USERNAME", "root"),
        "passwd"    : os.environ.get("NNIN_PASSWORD", "root"),
    }

    # Setup argument parser
    parser = ArgumentParser(
        description='Fetch room access data for a date range and create a table for pivot.',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--start', help='Start date YYYY-MM-DD')
    parser.add_argument('--end', help='End date YYYY-MM-DD')
    parser.add_argument(
        '--room',
        help='Room ID.  Default is Clean room %d' % CLEAN_ROOM_ID,
        default=CLEAN_ROOM_ID,
        type=int
    )
    args = parser.parse_args()

    start = args.start
    end = args.end
    roomid = args.room

    headers = ['Name', 'Start', 'End', 'Time']
    sql = '''
        select
            datetime,
            db_firstname,
            db_lastname,
            direction
        from cns_room_access_complete
        where
            userid > 0 and
            roomid = %s and
            datetime >= %s and
            datetime < %s
        order by userid, datetime
    '''.replace('\n',' ')

    connection = MySQLdb.connect(**SQL_DSN)
    cursor = connection.cursor()
    cursor.execute(sql, [roomid, start, end])

    lines = []
    current_line = ['' for _ in range(3)]
    current_name = None
    current_day = None
    for row in cursor:
        name = ' '.join([row[1], row[2]])
        day = row[0].timetuple().tm_yday
        if current_day is None:
            current_day = day
        direction = row[3]
        if current_name != name:
            if current_line[0]:
                lines.append(current_line)
                current_line = ['' for _ in range(3)]
                current_day = day
            current_line[0] = name
            current_name = name
        elif day != current_day:
            if current_line[0]:
                lines.append(current_line)
                current_line = ['' for _ in range(3)]
                current_line[0] = name
            current_day = day
        if direction == 'InDirection':
            if current_line[1]:
                lines.append(current_line)
                current_line = ['' for _ in range(3)]
                current_line[0] = name
            current_line[1] = row[0]
        else:
            current_line[2] = row[0]
    lines.append(current_line)
    print('\t'.join(headers))
    for line in lines:
        if line[1] and line[2]:
            delta = line[2] - line[1]
            line.append(delta.seconds)
        print('\t'.join([str(field) for field in line]))


if __name__ == '__main__':
    sys.exit(main())
