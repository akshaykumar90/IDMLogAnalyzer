-- LOGAN [LOG ANalyzer]
-- Schema for IDM Log Database

-- Download table holds all the entries stored in the log
create table download (
    name            text,
    filetype        text,
    date            text,
    time            text,
    filesize        integer
);
