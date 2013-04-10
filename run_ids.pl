#!  /usr/bin/perl -w

use strict;
use POSIX qw/strftime/;


while (1) {
    my $day_of_year  = strftime "%j", localtime;
    my $week_of_year = strftime "%W", localtime;

    my $log_string =  $day_of_year . $week_of_year;
    my $cmd_check_feeds = qq{ ./get_ids.py | md5sum };
    my $cmd_check_files = qq{ md5sum valid_ids };

    my $first_md5 = `$cmd_check_feeds`;
    my $second_md5 = `$cmd_check_files`;


    my $first_checksum = (split /\s/, $first_md5)[0];
    my $second_checksum = (split /\s/, $second_md5)[0];

    my $logfile_name = $log_string . ".log";
    if ( ($first_checksum ne $second_checksum) or !$second_checksum ) {
        `rm -f valid_ids`;
        `./get_ids.py > valid_ids`;
        my $date_string = scalar (localtime);
        $date_string .= "\n\n$date_string";
        `echo "$date_string" >> $logfile_name`;
        `./do_everything.py >> $logfile_name`;
    }

    sleep (900);
}
