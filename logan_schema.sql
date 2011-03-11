-- LOGAN [LOG ANalyzer]
-- Schema for IDM Log Database

-- Changelog records the date when the database was updated and
-- the no. of new items added
create table changelog (
    id              integer primary key autoincrement not null,
    update_date     text,
    new_items       integer
);

-- Download table holds all the entries stored in the log
create table download (
    name            text,
    extension       text,
    category        text,
    date            text,
    time            text,
    filesize        integer
);
