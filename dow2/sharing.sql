insert into sharingtypes values (1, 'shiploc', 'Ship Locations', 'The location of every ship (from system reports, terminal reports, traces, etc). Includes who paired with whom.');

insert into sharingmap values(1, 'shiploc');
insert into sharingmap values(1, 'meetings');

----------------------------------------------------------------------

insert into sharingtypes values (2, 'shipconfig', 'Ship Configurations', 'Modules, pods, artifacts, flag, power rank, and everything else derivable from a ship report.');

insert into sharingmap values(2, 'shipmodules');
insert into sharingmap values(2, 'shippods');
insert into sharingmap values(2, 'artifacts');
insert into sharingmap values(2, 'flags');
insert into sharingmap values(2, 'shippercents');
insert into sharingmap values(2, 'medicine');
insert into sharingmap values(2, 'shipmisc');

----------------------------------------------------------------------

insert into sharingtypes values(3, 'trade', 'Trade Resources', 'Values of trade resources (e.g. Quad Trees).');

insert into sharingmap values(3, 'trade');

----------------------------------------------------------------------

insert into sharingtypes values(4, 'shop', 'Shop Data', 'Modules and pods at shops.');

insert into sharingmap values(4, 'shopmodules');
insert into sharingmap values(4, 'shoppods');

----------------------------------------------------------------------

insert into sharingtypes values(5, 'plagues', 'Plague Levels', 'Plague levels.');
insert into sharingmap values(5, 'plagues');
