#!/bin/sh

cd /Path/to/tbg
turn=`psql -Aqt -d dow -c 'select max(turn) from turnupdate;'`
./get_sst.pl $turn
./purges.pl
#./updatepres.pl
./do_ships.pl
./rfat.pl
./rfat.pl
tar cf - turns/$turn ships/$turn | gzip | ccencrypt -K 'DowBackupPassphrase' > /Path/to/backup/dow-$turn
rm /Path/to/backup/dow-latest
ln -s /Path/to/backup/dow-$turn /Path/to/backup/dow-latest
