CREATE TABLE `online_players` (
	`id` text PRIMARY KEY NOT NULL,
	`owner_id` text NOT NULL,
	`secret_hash` text NOT NULL,
	`created` integer NOT NULL
);
--> statement-breakpoint
CREATE INDEX `players_owner` ON `online_players` (`owner_id`);