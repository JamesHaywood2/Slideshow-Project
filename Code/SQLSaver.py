import FileSupport as FP
import os
import sys
import time
import pprint

import sqlite3

#There is very little use for this file existing because the program exists as a stand-alone application.
#If you were to scale this program up to be like a web app/service then you could use this to greater effect.
#Example: 
#   - Get a new table based on each user account ID.
#   - Instead of storing the slideshow file paths, store a slideshow ID that is stored in the user's table.
#   - The file paths in the File table would correlate to the media on the server.
#   - This way the slideshows are now in the cloud and can be accessed from anywhere making the individual slideshow files kind of unnecessary.
#   - Could also store user ID's in the slideshow tables to keep track of who has permission to view/edit the slideshows.


#The path to the database will be in the cache directory
databasePath = os.path.join(FP.getUserCacheDir(), "SlideshowDatabase.db")

def createDatabase():
    # if os.path.exists(databasePath):
    #     return
    
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS `Slideshows` (
	`slideshow_filepath` TEXT NOT NULL UNIQUE,
	`slideshow_name` TEXT NOT NULL,
	`LoopSetting` TEXT NOT NULL DEFAULT 'Indefinite',
	`manual_controls` REAL NOT NULL DEFAULT 'False',
	`slide_shuffle` REAL NOT NULL DEFAULT 'False',
	`playlist_shuffle` REAL NOT NULL DEFAULT 'False',
	`playlist_duration` INTEGER DEFAULT '0',
	`tags` TEXT,
FOREIGN KEY(`tags`) REFERENCES `Tags`(`tag_name`)
);''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS `Song` (
	`id` integer primary key NOT NULL UNIQUE,
    `song_name` TEXT NOT NULL,  
	`song_order` INTEGER NOT NULL,
	`song_filepath_id` TEXT NOT NULL,
	`filetype` TEXT NOT NULL,
	`duration` INTEGER NOT NULL DEFAULT '0',
	`Slideshow_ID` TEXT NOT NULL,
FOREIGN KEY(`song_filepath_id`) REFERENCES `File`(`id`),
FOREIGN KEY(`Slideshow_ID`) REFERENCES `Slideshows`(`slideshow_filepath`)
);''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS `Slide` (
	`id` integer primary key NOT NULL UNIQUE,
	`slide_order` INTEGER NOT NULL,
	`transition` TEXT NOT NULL DEFAULT 'Default',
	`transition_speed` INTEGER NOT NULL,
	`slide_duration` INTEGER NOT NULL,
	`image_filepath_id` TEXT NOT NULL,
	`Slideshow_ID` TEXT NOT NULL,
FOREIGN KEY(`image_filepath_id`) REFERENCES `File`(`id`),
FOREIGN KEY(`Slideshow_ID`) REFERENCES `Slideshows`(`slideshow_filepath`)
);''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS `File` (
	`id` integer primary key NOT NULL UNIQUE,
	`file_path` TEXT NOT NULL UNIQUE,
	'file_name' TEXT NOT NULL,
	`file_type` TEXT NOT NULL
);''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS `Tags` (
        `tag_name` integer primary key NOT NULL UNIQUE,
        `slideshow_list` TEXT NOT NULL,
    FOREIGN KEY(`slideshow_list`) REFERENCES `Slideshows`(`slideshow_filepath`)
    );''')
    

    # c.execute("FOREIGN KEY(`tags`) REFERENCES `Tags`(`tag_name`);")
    # c.execute("FOREIGN KEY(`song_filepath_id`) REFERENCES `File`(`id`);")
    # c.execute("FOREIGN KEY(`Slideshow_ID`) REFERENCES `Slideshows`(`slideshow_filepath`);")
    # c.execute("FOREIGN KEY(`image_filepath_id`) REFERENCES `File`(`id`);")
    # c.execute("FOREIGN KEY(`Slideshow_ID`) REFERENCES `Slideshows`(`slideshow_filepath`);")
    # c.execute("FOREIGN KEY(`slideshow_list`) REFERENCES `Slideshows`(`slideshow_filepath`);")


    conn.commit()

    conn.close()
    return

def getNewSlideID():
    #Get a new unused slide id
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()
    c.execute("SELECT MAX(id) FROM Slide")
    result = c.fetchone()


def saveSlideshow(slideshow):
    #If the slideshow is a path to a slideshow file, load the slideshow from the file first.
    if isinstance(slideshow, str):
        #Check the file extension
        if not slideshow.endswith(".pyslide"):
            return False
        #Check if the file exists
        if not os.path.exists(slideshow):
            return False
        #Load the slideshow
        slideshow = FP.Slideshow(slideshow)
    elif not isinstance(slideshow, FP.Slideshow):
        return False
        

    #Print the slideshow object
    # pprint.pprint(slideshow.__dict__)
    
    #Get the slideshow information
    slideshowPath = slideshow.getSaveLocation()
    slideshowName = slideshow.name
    loopSetting = slideshow.loopSettings
    manualControls = slideshow.manual
    slideShuffle = slideshow.shuffle

    slideList = slideshow.getSlides()
    playlist = slideshow.getPlaylist()

    playlistShuffle = playlist.shuffle
    playlistDuration = playlist.getDuration()

    tags = slideshow.tags

    #Connect to the database
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()

    filesInProject = slideshow.filesInProject

    for slide in slideList:
        try:
            s = FP.Slide(slide['imagePath'])
            s.__dict__.update(slide)
            slideList[slideList.index(slide)] = s
            slide = s
        except:
            pass


        #Append the imagePath to the filesinproject list
        if slide.imagePath not in filesInProject:
            filesInProject.append(slide.imagePath)
        
        #Update the slide in slidelist with the new SlideObject
        slideList[slideList.index(slide)] = slide

    for song in playlist.songs:
        try:
            s = FP.Song(song['filePath'])
            s.__dict__.update(song)
            playlist.songs[playlist.songs.index(song)] = s
            song = s
        except:
            pass

        #Append the songPath to the filesinproject list
        if song.filePath not in filesInProject:
            filesInProject.append(song.filePath)

        #Update the song in playlist with the new SongObject
        playlist.songs[playlist.songs.index(song)] = song

    #Check if the slideshow is already in the database
    c.execute("SELECT slideshow_filepath FROM Slideshows WHERE slideshow_filepath = ?", (slideshowPath,))
    result = c.fetchone()
    if result != None:
        #Update the slideshow
        c.execute("UPDATE Slideshows SET slideshow_name = ?, LoopSetting = ?, manual_controls = ?, slide_shuffle = ?, playlist_shuffle = ?, playlist_duration = ? WHERE slideshow_filepath = ?", (slideshowName, loopSetting, manualControls, slideShuffle, playlistShuffle, playlistDuration, slideshowPath))
    else:
        #Insert the slideshow
        c.execute("INSERT INTO Slideshows (slideshow_filepath, slideshow_name, LoopSetting, manual_controls, slide_shuffle, playlist_shuffle, playlist_duration) VALUES (?, ?, ?, ?, ?, ?, ?)", (slideshowPath, slideshowName, loopSetting, manualControls, slideShuffle, playlistShuffle, playlistDuration))

    
    #Clear the tags for the slideshow
    c.execute("UPDATE Slideshows SET tags = NULL WHERE slideshow_filepath = ?", (slideshowPath,))
    
    c.execute("DELETE FROM Slide WHERE Slideshow_ID = ?", (slideshowPath,))
    c.execute("DELETE FROM Song WHERE Slideshow_ID = ?", (slideshowPath,))

    #Insert the files into the database
    for file in filesInProject:
        #Check if the file is already in the database
        c.execute("SELECT id FROM File WHERE file_path = ?", (file,))
        result = c.fetchone()
        if result != None:
            continue
        
        fileName = os.path.basename(file)
        fileType = "." + file.split(".")[-1]

        c.execute("INSERT INTO File (file_path, file_name, file_type) VALUES (?, ?, ?)", (file, fileName, fileType))
        #Get the file id of the file that matches what was just inserted
        c.execute("SELECT id FROM File WHERE file_path = ?", (file,))
        fileID = c.fetchone()[0]
        #Insert the file id into the project_file_list for the slideshow
        # c.execute("UPDATE Slideshows SET project_file_list = ? WHERE slideshow_filepath = ?", (fileID, slideshowPath))

    #Insert slides into the database
    for slide in slideList:
        imagePath = slide.imagePath
        #Get the file id
        c.execute("SELECT id FROM File WHERE file_path = ?", (imagePath,))
        imageID = c.fetchone()[0]
        slideOrder = slide.slideID
        transition = slide.transition
        transitionSpeed = slide.transitionSpeed
        slideDuration = slide.duration
        #If slide.slideDB_ID is not None, then the slide is already in the database and should be updated
        if slide.slideDB_ID != None:
            print(f"Updating slide: {slide.slideDB_ID}")
            c.execute("UPDATE Slide SET slide_order = ?, transition = ?, transition_speed = ?, slide_duration = ?, image_filepath_id = ?, Slideshow_ID = ? WHERE id = ?", (slideOrder, transition, transitionSpeed, slideDuration, imageID, slideshowPath, slide.slideDB_ID)) 

        print(f"Inserting slide: {slideOrder}, {transition}, {transitionSpeed}, {slideDuration}, {imageID}, {slideshowPath}")
        c.execute("INSERT INTO Slide (slide_order, transition, transition_speed, slide_duration, image_filepath_id, Slideshow_ID) VALUES (?, ?, ?, ?, ?, ?)", (slideOrder, transition, transitionSpeed, slideDuration, imageID, slideshowPath))
        #Get the slide id of the slide that matches what was just inserted
        c.execute("SELECT id FROM Slide WHERE slide_order = ? AND Slideshow_ID = ?", (slideOrder, slideshowPath))
        slideID = c.fetchone()[0]
        #Update the slideList with the new slideID
        slideList[slideList.index(slide)].slideDB_ID = slideID

        # c.execute("UPDATE Slideshows SET Slidelist_ids = ? WHERE slideshow_filepath = ?", (slideID, slideshowPath))
        # c.execute("INSERT INTO Slideshows (Slidelist_ids) VALUES (?) WHERE slideshow_filepath = ?", (slideID, slideshowPath))


    #Insert songs into the database
    for song in playlist.songs:
        songPath = song.filePath
        #Get the file id
        c.execute("SELECT id FROM File WHERE file_path = ?", (songPath,))
        songID = c.fetchone()[0]
        #Song order is the index in the playlist
        songOrder = playlist.songs.index(song)
        duration = song.duration
        filetype = song.fileType
        songName = song.name
        #If song.songDB_ID is not None, then the song is already in the database and should be updated
        if song.songDB_ID != None:
            print(f"Updating song: {song.songDB_ID}")
            c.execute("UPDATE Song SET song_order = ?, song_filepath_id = ?, duration = ?, filetype = ?, song_name = ?, Slideshow_ID = ? WHERE id = ?", (songOrder, songID, duration, filetype, songName, slideshowPath, song.songDB_ID))
        
        print(f"Inserting song: {songOrder}, {songID}, {duration}, {filetype}")
        c.execute("INSERT INTO Song (song_order, song_filepath_id, duration, filetype, song_name, Slideshow_ID) VALUES (?, ?, ?, ?, ?, ?)", (songOrder, songID, duration, filetype, songName, slideshowPath))
        #Get the song id of the song that matches what was just inserted
        c.execute("SELECT id FROM Song WHERE song_order = ? AND Slideshow_ID = ?", (songOrder, slideshowPath))
        songID = c.fetchone()[0]
        #Update the song with the new songID
        song.songDB_ID = songID

        # c.execute("UPDATE Slideshows SET playlist_song_ids = ? WHERE slideshow_filepath = ?", (songID, slideshowPath))
        # c.execute("INSERT INTO Slideshows (playlist_song_ids) VALUES (?) WHERE slideshow_filepath = ?", (songID, slideshowPath))

    #Insert tags into the database
    for tag in tags:
        #Check if the tag is already in the database
        c.execute("SELECT tag_name FROM Tags WHERE tag_name = ?", (tag,))
        result = c.fetchone()
        if result != None:
            continue
        c.execute("INSERT INTO Tags (tag_name, slideshow_list) VALUES (?, ?)", (tag, slideshowPath))

        c.execute("UPDATE Slideshows SET tags = ? WHERE slideshow_filepath = ?", (tag, slideshowPath))

    conn.commit()
    conn.close()

def validateDatabase():
    """Check if the slideshows in the database are valid and existing. If they are not, remove them from the database."""
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()

    c.execute("SELECT slideshow_filepath FROM Slideshows")
    slideshows = c.fetchall()

    for slideshow in slideshows:
        if not os.path.exists(slideshow[0]):
            print("Removing slideshow")
            c.execute("DELETE FROM Slideshows WHERE slideshow_filepath = ?", (slideshow[0],))
        
    conn.commit()
    conn.close()

def getSlideshows():
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()

    c.execute("SELECT slideshow_filepath FROM Slideshows")
    slideshows = c.fetchall()
    conn.close()

    for slideshow in slideshows:
        slideshow = FP.Slideshow(slideshow[0])

    return slideshows

def getSlideshow(slideshowPath):
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()

    c.execute("SELECT * FROM Slideshows WHERE slideshow_filepath = ?", (slideshowPath,))
    slideshow = c.fetchone()
    print(slideshow)

    


    # slideshow = FP.Slideshow(slideshow[0])
    return slideshow


# createDatabase()
# saveSlideshow(r"C:\Users\JamesH\OneDrive - uah.edu\CS499\TestImages3\exported_assets_Kitty - Copy - Copy\kitty-TEST.pyslide")
# saveSlideshow(r"C:\Users\JamesH\OneDrive - uah.edu\CS499\TestImages3\Kitty - Copy.pyslide")
# saveSlideshow(r"C:\Users\JamesH\OneDrive - uah.edu\CS499\TestImages3\Kitty.pyslide")
saveSlideshow(r"C:\Users\JamesH\Downloads\exported_assets_test1_2024-04-09_20-45-57\test1.pyslide")
# validateDatabase()
# getSlideshow(r"C:\Users\JamesH\OneDrive - uah.edu\CS499\TestImages3\exported_assets_Kitty - Copy - Copy\kitty-TEST.pyslide")
    

    


