SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

CREATE TABLE `nkhtm` (
  `guild_id` varchar(255) NOT NULL,
  `channel_id` varchar(255) NOT NULL,
  `page` varchar(3) NOT NULL,
  `timestamp` double NOT NULL,
  `num` int(3) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `voice` (
  `guild_id` varchar(255) NOT NULL,
  `channel_id` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

ALTER TABLE `nkhtm`
  ADD PRIMARY KEY (`guild_id`);

ALTER TABLE `voice`
  ADD PRIMARY KEY (`guild_id`);
COMMIT;
