-- Create a table
CREATE TABLE CS50Data (
    Year INTEGER,
    Score TEXT,
    Winner TEXT,
    Harvard_Yards INTEGER,
    Yale_Yards INTEGER,
    H_Turnovers INTEGER,
    Y_Turnovers INTEGER,
    H_First_Downs INTEGER,
    Y_First_Downs INTEGER
);

-- Insert data into the table
INSERT INTO CS50Data (Year, Score, Winner, Harvard_Yards, Yale_Yards, H_Turnovers, Y_Turnovers, H_First_Downs, Y_First_Downs)
VALUES
    (2010, '28-21', 'Harvard', 180, 329, 1, 1, 10, 19),
    (2011, '45-7', 'Harvard', 506, 302, 0, 3, 24, 13),
    (2012, '34-24', 'Harvard', 518, 351, 1, 2, 25, 14),
    (2013, '34-7', 'Harvard', 425, 279, 1, 2, 22, 18),
    (2014, '31-24', 'Harvard', 439, 430, 2, 2, 19, 25),
    (2015, '38-19', 'Harvard', 508, 444, 1, 0, 27, 27),
    (2016, '21-14', 'Yale', 329, 304, 2, 0, 17, 20),
    (2017, '24-3', 'Yale', 164, 295, 4, 1, 26, 14),
    (2018, '45-27', 'Harvard', 578, 411, 0, 2, 23, 23),
    (2019, '50-43', 'Yale', 498, 564, 2, 2, 17, 31),
    (2020, 'COVID', 'N/A', NULL, NULL, NULL, NULL, NULL, NULL),
    (2021, '34-31', 'Harvard', 317, 417, 2, 3, 17, 25),
    (2022, '19-14', 'Yale', 288, 363, 4, 1, 12, 19),
    (2023, '23-18', 'Yale', 318, 260, 2, 2, 16, 20),
    (2024, '34-29', 'Yale', 349, 503, 2, 0, 19, 22);
