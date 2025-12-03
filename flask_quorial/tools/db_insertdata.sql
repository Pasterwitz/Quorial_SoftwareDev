/* Seed data for Quorial chat application */

/* Default demo users (password: Go4one!) */
INSERT INTO user (username, password) VALUES
    ('1234', 'pbkdf2:sha256:260000$TE7rfiidZO86orwh$7e0f8049432d0ab7842f45e2d1de68ed3c61fbd01655ba9a5d093e350cf9edfa'),
    ('2345', 'pbkdf2:sha256:260000$TE7rfiidZO86orwh$7e0f8049432d0ab7842f45e2d1de68ed3c61fbd01655ba9a5d093e350cf9edfa'),
    ('guest', 'pbkdf2:sha256:260000$MzkPXrPPnl7F5dN7$11fed544bf7be1e520e908eaaea1222d62e3b567b36853a68116b617ae75882f');
