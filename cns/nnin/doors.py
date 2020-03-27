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
from datetime import str
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter

CLEAN_ROOM_ID = 24  # Room ID from NNIN database

def main(argv=None):
    '''
    Fetch room access data for a date range and create a table suitable for pivot
    '''
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    # Setup argument parser
    parser = ArgumentParser(
        description='Fetch room access data for a date range and create a table for pivot',
        formatter_class=ArgumentDefaultsHelpFormatter,
        add_help=False
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

    headers = ['Name', 'Start', 'End', 'Time', 'Hours']
    sql = '''
        select
            datetime,
            db_firstname,
            db_lastname,
            direction
        from cns_room_access_complete
        where
            userid > 0 and
            and roomid = %s and
            datetime >= %s and
            datetime < %s
        order by userid, datetime
    '''.translate(None,'\n')

    connection = MySQLdb.connect(**SQL_DSN)
    cursor = connection.cursor()
    cursor.execute(sql, [roomid, start, end])

    lines = []
    current_line = ['' for _ in range(3)]
    current_name = None
    current_day = None
    for row in cursor:
        data = []
        name = ' '.join([row[1], row[2]])
        day = row[0].timetuple().tm_yday
        direction = row[3]
        if current_name != name:
            if current_line:
                lines.append(current_line)
                current_line = ['' for _ in range(3)]
                current_line[0] = name
            current_name = name
        if day != current_day:
            if current_line:
                lines.append(current_line)
                current_line = ['' for _ in range(3)]
                current_line[0] = name
            current_day = day
        if direction = 'InDirection':
            if current_line[1]:
                lines.append(current_line)
                current_line = ['' for _ in range(3)]
                current_line[0] = name
            current_line[1] = row[0]
        else:
            current_line[2] = row[0]




    print('\t'.join(headers))
    for line in lines:
        print('\t'.join(line))