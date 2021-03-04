BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "limbo" (
	"guild_id"	TEXT,
	"user_id"	TEXT,
	"roles_ids"	TEXT
);
CREATE TABLE IF NOT EXISTS "logs" (
	"guild_id"	TEXT,
	"channel_id"	TEXT
);
CREATE TABLE IF NOT EXISTS "welcomer" (
	"guild_id"	TEXT,
	"msg"	TEXT,
	"channel_id"	TEXT
);
CREATE TABLE IF NOT EXISTS "tag" (
	"guild_id"	TEXT,
	"author_id"	TEXT,
	"names"	TEXT,
	"content"	TEXT
);
CREATE TABLE IF NOT EXISTS "giveyou" (
	"guildid"	INTEGER,
	"name"	TEXT,
	"rolename"	TEXT,
	"roleid"	INTEGER
);
CREATE TABLE IF NOT EXISTS "persistentroles" (
	"guildid"	INTEGER,
	"userid"	INTEGER,
	"roles"	TEXT
);
CREATE TABLE IF NOT EXISTS "banned" (
	"guildid"	INTEGER,
	"userid"	INTEGER
);
CREATE TABLE IF NOT EXISTS "prefixes" (
	"guildid"	INTEGER,
	"prefix"	BLOB
);
CREATE TABLE IF NOT EXISTS "giveme" (
	"guildid"	INTEGER,
	"rankname"	TEXT,
	"rankid"	INTEGER,
	"name"	TEXT,
	"rolename"	TEXT,
	"roleid"	INTEGER
);
CREATE TABLE IF NOT EXISTS "colourme" (
	"guildid"	INTEGER,
	"rankname"	TEXT,
	"rankid"	INTEGER,
	"name"	TEXT,
	"rolename"	TEXT,
	"roleid"	INTEGER
);
CREATE TABLE IF NOT EXISTS "mutes" (
	"guildid"	INTEGER,
	"user"	INTEGER,
	"roles"	TEXT,
	"starttime"	DATETIME,
	"endtime"	DATETIME
);
CREATE TABLE IF NOT EXISTS "strikes" (
	"strikeid"	INTEGER,
	"guildid"	INTEGER,
	"user"	INTEGER,
	"moderator"	TEXT,
	"action"	TEXT,
	"reason"	TEXT
);
COMMIT;
