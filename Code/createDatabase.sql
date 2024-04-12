CREATE TABLE IF NOT EXISTS `Slideshows` (
    'slideshow_ID' INTEGER primary key NOT NULL UNIQUE,
	`slideshow_name` TEXT NOT NULL,
	`LoopSetting` TEXT NOT NULL DEFAULT 'Indefinite',
	`manual_controls` REAL NOT NULL DEFAULT 'False',
	`slide_shuffle` REAL NOT NULL DEFAULT 'False',
	`playlist_shuffle` REAL NOT NULL DEFAULT 'False',
	`playlist_duration` INTEGER DEFAULT '0',
	`tags` TEXT,
FOREIGN KEY(`tags`) REFERENCES `Tags`(`tag_name`)
);
CREATE TABLE IF NOT EXISTS `Song` (
	`id` integer primary key NOT NULL UNIQUE,
    `song_name` TEXT NOT NULL,  
	`song_order` INTEGER NOT NULL,
	`song_filepath_id` TEXT NOT NULL,
	`filetype` TEXT NOT NULL,
	`duration` INTEGER NOT NULL DEFAULT '0',
	`Slideshow_ID` Integer NOT NULL,
FOREIGN KEY(`song_filepath_id`) REFERENCES `File`(`id`),
FOREIGN KEY(`Slideshow_ID`) REFERENCES `Slideshows`(`slideshow_ID`)
);
CREATE TABLE IF NOT EXISTS `Slide` (
	`id` integer primary key NOT NULL UNIQUE,
	`slide_order` INTEGER NOT NULL,
	`transition` TEXT NOT NULL DEFAULT 'Default',
	`transition_speed` INTEGER NOT NULL,
	`slide_duration` INTEGER NOT NULL,
	`image_filepath_id` TEXT NOT NULL,
	`Slideshow_ID` INTEGER NOT NULL,
FOREIGN KEY(`image_filepath_id`) REFERENCES `File`(`id`),
FOREIGN KEY(`Slideshow_ID`) REFERENCES `Slideshows`(`slideshow_ID`)
);
CREATE TABLE IF NOT EXISTS `File` (
	`id` integer primary key NOT NULL UNIQUE,
	`file_path` TEXT NOT NULL UNIQUE,
	'file_name' TEXT NOT NULL,
	`file_type` TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS `Tags` (
        `tag_name` integer primary key NOT NULL UNIQUE,
        `slideshow_list` TEXT NOT NULL,
    FOREIGN KEY(`slideshow_list`) REFERENCES `Slideshows`(`slideshow_ID`)
    );