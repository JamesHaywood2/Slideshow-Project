import re
from tkinter import filedialog
import FileSupport as FP
import os
import sys
import time
import json
import pprint

import sqlite3
import sqlparse

#There is very little use for this file existing because the program exists as a stand-alone application.
#If you were to scale this program up to be like a web app/service then you could use this to greater effect.
#Example: 
#   - Get a new table based on each user account ID.
#   - Instead of storing the slideshow file paths, store a slideshow ID that is stored in the user's table.
#   - The file paths in the File table would correlate to the media on the server.
#   - This way the slideshows are now in the cloud and can be accessed from anywhere making the individual slideshow files kind of unnecessary.
#   - Could also store user ID's in the slideshow tables to keep track of who has permission to view/edit the slideshows.


#The path to the database will be in the cache directory
databasePath = os.path.join(FP.getUserCacheDir(), "SlideshowDatabase2.db")

def clearDatabase():
    #Clear the database
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()
    c.execute("DELETE FROM Slideshows")
    c.execute("DELETE FROM Slide")
    c.execute("DELETE FROM Song")
    c.execute("DELETE FROM File")
    c.execute("DELETE FROM FileRecord")
    c.execute("DELETE FROM Tags")
    c.execute("DELETE FROM TagRecord")
    conn.commit()
    conn.close()

def resetDatabase():
    #Clear the database
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS Slideshows")
    c.execute("DROP TABLE IF EXISTS Slide")
    c.execute("DROP TABLE IF EXISTS Song")
    c.execute("DROP TABLE IF EXISTS File")
    c.execute("DROP TABLE IF EXISTS FileRecord")
    c.execute("DROP TABLE IF EXISTS Tags")
    c.execute("DROP TABLE IF EXISTS TagRecord")
    conn.commit()
    conn.close()
    createDatabase()

def createDatabase():
    # if os.path.exists(databasePath):
    #     return
    
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS `Slideshows` (
    'slideshow_ID' integer primary key NOT NULL UNIQUE,
	`slideshow_name` TEXT NOT NULL UNIQUE,
	`LoopSetting` TEXT NOT NULL DEFAULT 'Indefinite',
	`manual_controls` REAL NOT NULL DEFAULT 'False',
	`slide_shuffle` REAL NOT NULL DEFAULT 'False',
	`playlist_shuffle` REAL NOT NULL DEFAULT 'False',
	`playlist_duration` INTEGER DEFAULT '0',
    'LastModified' TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS `Song` (
	`id` integer primary key NOT NULL UNIQUE,
    `song_name` TEXT NOT NULL,  
	`song_order` INTEGER NOT NULL,
	`SongRecord_id` INTEGER NOT NULL,
	`filetype` TEXT NOT NULL,
	`duration` INTEGER NOT NULL DEFAULT '0',
	`Slideshow_ID` Integer NOT NULL,
FOREIGN KEY(`SongRecord_id`) REFERENCES `FileRecord`(`id`),
FOREIGN KEY(`Slideshow_ID`) REFERENCES `Slideshows`(`slideshow_ID`)
);''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS `Slide` (
	`id` integer primary key NOT NULL UNIQUE,
	`slide_order` INTEGER NOT NULL,
	`transition` TEXT NOT NULL DEFAULT 'Default',
	`transition_speed` INTEGER NOT NULL,
	`slide_duration` INTEGER NOT NULL,
	`SlideRecord_id` INTEGER NOT NULL,
	`Slideshow_ID` Integer NOT NULL,
FOREIGN KEY(`SlideRecord_id`) REFERENCES `FileRecord`(`id`),
FOREIGN KEY(`Slideshow_ID`) REFERENCES `Slideshows`(`slideshow_ID`)
);''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS `File` (
	`id` integer primary key NOT NULL UNIQUE,
	`file_path` TEXT NOT NULL UNIQUE,
	'file_name' TEXT NOT NULL,
	`file_type` TEXT NOT NULL
);''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS 'FileRecord' (
    'id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'file_id' INTEGER NOT NULL,
    'slideshow_id' INTEGER NOT NULL,
    'RecordType' TEXT NOT NULL DEFAULT 'Misc',
    'FileName' TEXT NOT NULL,
FOREIGN KEY('file_id') REFERENCES 'File'('id'),
FOREIGN KEY('slideshow_id') REFERENCES 'Slideshows'('slideshow_ID')
);''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS `Tags` (
        `tag_id` INTEGER primary key NOT NULL UNIQUE,
        `tag_name` TEXT NOT NULL UNIQUE
    );''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS `TagRecord` (
        `id` integer primary key NOT NULL UNIQUE,
        `tag_id` INTEGER NOT NULL,
        `slideshow_id` INTEGER NOT NULL,
    FOREIGN KEY(`tag_id`) REFERENCES `Tags`(`tag_id`),
    FOREIGN KEY(`slideshow_id`) REFERENCES `Slideshows`(`slideshow_ID`)
    );''')

    # c.execute("FOREIGN KEY(`tags`) REFERENCES `Tags`(`tag_name`);")
    # c.execute("FOREIGN KEY(`SongRecord_id`) REFERENCES `File`(`id`);")
    # c.execute("FOREIGN KEY(`SlideRecord_id`) REFERENCES `File`(`id`);")

    #Create a trigger to enforce the record type to be one of the three options (Slide, Song, Misc) default is Misc
    c.execute('''CREATE TRIGGER IF NOT EXISTS enforce_record_type
    BEFORE INSERT ON FileRecord
    BEGIN
        UPDATE FileRecord SET RecordType = 'Misc' WHERE NEW.RecordType NOT IN ('Slide', 'Song', 'Misc');
    END;''')
                    

    conn.commit()
    conn.close()
    return


def renameSlideshow(slideshowID:int, newName:str) -> bool:
    print(f"Renaming slideshow: {slideshowID} to {newName}")
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()

    settingsToTest = [newName]
    for setting in settingsToTest:
        # print(setting)
        if sqlProtector(setting):
            print("Injection detected")
            return False
    #Check if the name is already in use
    c.execute("SELECT slideshow_name FROM Slideshows WHERE slideshow_name = ?", (newName,))
    name = c.fetchone()
    if name != None:
        print("Name already in use")
        return False
    #Name not in use - update the name
    c.execute("UPDATE Slideshows SET slideshow_name = ? WHERE slideshow_ID = ?", (newName, slideshowID))
    conn.commit()
    conn.close()
    return True

def saveSlideshow(slideshow, fromFile=False, toFile=False):
    """Will take a slideshow object and then save it to the database."""
    #If the slideshow is a path to a slideshow file, load the slideshow from the file first.
    if isinstance(slideshow, str):
        #Check the file extension
        if not slideshow.endswith(".pyslide"):
            print("Invalid file extension")
            return False
        #Check if the file exists
        if not os.path.exists(slideshow):
            print("File does not exist")
            return False
        #Load the slideshow
        slideshow = FP.Slideshow(slideshow)
        fromFile = True
    elif not isinstance(slideshow, FP.Slideshow):
        print("Invalid slideshow object")
        return False
    
    tempSaveLocation = ""
    saveLocation = ""
    if toFile:
        tempSaveLocation = slideshow.getSaveLocation()
        saveLocation = filedialog.asksaveasfilename(defaultextension=".pyslide", filetypes=[("PySlide Files", "*.pyslide")])
        if saveLocation == "":
            print("No file selected")
            return False
        
    #Get the slideshow information
    slideshowPath = slideshow.getSaveLocation()
    slideshowName = slideshow.name
    loopSetting = slideshow.loopSettings
    manualControls = slideshow.manual
    slideShuffle = slideshow.shuffle
    slideshowID = slideshow.slideshowID

    slideList = slideshow.getSlides()
    playlist = slideshow.getPlaylist()

    playlistShuffle = playlist.shuffle
    playlistDuration = playlist.getDuration()

    tags = slideshow.tags

    pprint.pprint(slideshow)

    # Get the current date
    current_date = time.strftime('%Y-%m-%d %H:%M:%S')

    #Connect to the database
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()

    filesInProject = slideshow.filesInProject

    settingsToTest = [slideshowPath, slideshowName, loopSetting, slideshowPath]
    for setting in settingsToTest:
        # print(setting)
        if sqlProtector(setting):
            return False
        
    if fromFile:
        print(f"Saving from a file: {slideshowPath}")
        slideshowID = None
        slideshow.slideshowID = None
        FP.set_relative_project_path(slideshow.getSaveLocation())

        #Check if the name is already in use
        c.execute("SELECT slideshow_name FROM Slideshows WHERE slideshow_name = ?", (slideshowName,))
        name_id = c.fetchone()
        if name_id != None:
            print(f"Name already in use: {slideshowName}")
            #Make a new name
            i = 1
            while True:
                newName = f"{slideshowName} ({i})"
                c.execute("SELECT slideshow_ID FROM Slideshows WHERE slideshow_name = ?", (newName,))
                name_id = c.fetchone()
                if name_id == None:
                    break
                i += 1
            print(f"New name: {newName}")
            slideshow.name = newName
            slideshowName = slideshow.name
            slideshow.setSaveLocation("Saved To Database")

    #Check if the slideshowID is already in use
    c.execute("SELECT slideshow_ID FROM Slideshows WHERE slideshow_ID = ?", (slideshowID,))
    id = c.fetchone()
    if id == None:
        #SlideshowID is not in use.
        slideshowID = None
        slideshow.slideshowID = None
        print(f"ID was not in use: {slideshowID}")
    else:
        #SlideshowID is in use.
        slideshowID = id[0]
        slideshow.slideshowID = slideshowID
        print(f"ID was in use: {slideshowID}")

    #Check if the name is already in use
    c.execute("SELECT slideshow_ID FROM Slideshows WHERE slideshow_name = ?", (slideshowName,))
    name_id = c.fetchone()
    if name_id == None:
        #Name is not in use.
        name_id = None
        print(f"Name was not in use: {slideshowName}")
    else:
        #Name is in use.
        name_id = name_id[0]
        print(f"Name was in use: {slideshowName}")

    print(f"\nDoing Name: {name_id} ID: {slideshowID} Check")
    #If both name and ID None then this is a branch new slideshow. - Insert the slideshow into the database.
    if name_id == None and slideshowID == None:
        c.execute('''INSERT INTO Slideshows
                  (slideshow_name, LoopSetting, manual_controls, slide_shuffle, playlist_shuffle, playlist_duration, LastModified) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (slideshowName, loopSetting, manualControls, slideShuffle, playlistShuffle, playlistDuration, current_date))
        #Get the slideshow ID of the slideshow that matches what was just inserted
        c.execute("SELECT slideshow_ID FROM Slideshows WHERE slideshow_name = ?", (slideshowName,))
        slideshowID = c.fetchone()[0]
        #Update the slideshow with the new slideshowID
        slideshow.slideshowID = slideshowID
        print(f"New slideshow ID: {slideshowID}")
    
    #If ID is in use, but name is not then the slideshow was renamed. - Update the name in the database.
    elif name_id == None and slideshowID != None:
        c.execute('''UPDATE Slideshows
                  SET slideshow_name = ?, LoopSetting = ?, manual_controls = ?, slide_shuffle = ?, playlist_shuffle = ?, playlist_duration = ?, LastModified = ? WHERE slideshow_ID = ?''',
                  (slideshowName, loopSetting, manualControls, slideShuffle, playlistShuffle, playlistDuration, current_date, slideshowID))
        print(f"Renaming slideshow: {slideshowID} to new name: {slideshowName}")

    #It is impossible for a name to be in use and not have an ID because the name is the primary key.
    elif name_id != None and slideshowID == None:
        print("Error: Name is in use but ID is not. Should be impossible.")
        return False
    
    #If both name and ID are in use and match, then the slideshow is already in the database. - Update the slideshow in the database.
    elif name_id != None and slideshowID != None and name_id == slideshowID:
        c.execute('''UPDATE Slideshows
                  SET slideshow_name = ?, LoopSetting = ?, manual_controls = ?, slide_shuffle = ?, playlist_shuffle = ?, playlist_duration = ?, LastModified = ? WHERE slideshow_ID = ?''',
                  (slideshowName, loopSetting, manualControls, slideShuffle, playlistShuffle, playlistDuration, current_date, slideshowID))
        print(f"Updating slideshow: {slideshowID}")

    #If both name and ID are in use but don't match, then the name is already in use. - Make a new name and insert the slideshow into the database.
    elif name_id != None and slideshowID != None and name_id != slideshowID:
        print(f"Name and ID are in use but don't match. Name: {name_id} ID: {slideshowID}")
        while True:
            i = 1
            newName = f"{slideshowName} ({i})"
            c.execute("SELECT slideshow_ID FROM Slideshows WHERE slideshow_name = ?", (newName,))
            name_id = c.fetchone()
            if name_id == None:
                break
            i += 1
        print(f"New name: {newName}")
        slideshow.name = newName
        slideshowName = slideshow.name
        c.execute('''INSERT INTO Slideshows
                    (slideshow_name, LoopSetting, manual_controls, slide_shuffle, playlist_shuffle, playlist_duration, LastModified) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (slideshowName, loopSetting, manualControls, slideShuffle, playlistShuffle, playlistDuration, current_date))
        #Get the slideshow ID of the slideshow that matches what was just inserted
        c.execute("SELECT slideshow_ID FROM Slideshows WHERE slideshow_name = ?", (slideshowName,))
        slideshowID = c.fetchone()[0]
        #Update the slideshow with the new slideshowID
        slideshow.slideshowID = slideshowID
        print(f"New slideshow ID: {slideshowID}")
    else:
        print("Error: Unknown error")
        return False
        

    slidePathList = []
    for slide in slideList:
        try:
            s = FP.Slide(slide['imagePath'])
            s.__dict__.update(slide)
            slideList[slideList.index(slide)] = s
            slide = s
        except:
            pass

        #Locate the file in the system. We either want it to be at the full path or the relative path.
        loc = FP.file_loc(slide.imagePath, FP.relative_project_path)
        if loc == 1:
            slide.imagePath = FP.file_check(slide.imagePath, FP.relative_project_path)
        else:
            #We want to update the filepath when it is in the projectPath. Otherwise just keep the full one and hope for the best. lmao.
            pass

        # #Append the imagePath to the filesinproject list
        if slide.imagePath not in slidePathList:
            slidePathList.append(slide.imagePath)
        
        #Update the slide in slidelist with the new SlideObject
        slideList[slideList.index(slide)] = slide

    songPathList = []
    for song in playlist.songs:
        if not isinstance(song, FP.Song):
            try:
                path = song['filePath']
            except:
                path = song.filePath
            s = FP.Song(path)
            s.__dict__.update(song)
            playlist.songs[playlist.songs.index(song)] = s
            song = s

        #Locate the file in the system. We either want it to be at the full path or the relative path.
        loc = FP.file_loc(song.filePath, FP.relative_project_path)
        if loc == 1:
            song.filePath = FP.file_check(song.filePath, FP.relative_project_path)
        else:
            #We want to update the filepath when it is in the projectPath. Otherwise just keep the full one and hope for the best. lmao.
            pass

        #Append the songPath to the songPathList
        if song.filePath not in songPathList:
            songPathList.append(song.filePath)

        #Update the song in playlist with the new SongObject
        playlist.songs[playlist.songs.index(song)] = song

    #Combine the filesInProject list with the slidePathList and songPathList
    files = filesInProject + slidePathList + songPathList
    files = list(set(files))

    #Insert the files into the database
    for file in files:

        #locate the file in the system. We either want it to be at the full path or the relative path.
        loc = FP.file_loc(file, FP.relative_project_path)
        if loc == 1:
            file = FP.file_check(file, FP.relative_project_path)
        else:
            #We want to update the filepath when it is in the projectPath. Otherwise just keep the full one and hope for the best. lmao.
            pass
        
        #Check if the file is already in the database
        c.execute("SELECT id FROM File WHERE file_path = ?", (file,))
        fileID = c.fetchone()
        if fileID == None:
            #We need to insert the file into the database.
            fileName = os.path.basename(file)
            fileType = file.split(".")[-1]
            c.execute("INSERT INTO File (file_path, file_name, file_type) VALUES (?, ?, ?)", (file, fileName, fileType))
            #Get the file id of the file that matches what was just inserted
            c.execute("SELECT id FROM File WHERE file_path = ?", (file,))
            fileID = c.fetchone()[0]
        else:
            #File is already in the database so we don't need to worry about it.
            pass

        #Check if the file is a slide, song, or misc
        if file in slidePathList:
            recordType = "Slide"
        elif file in songPathList:
            recordType = "Song"
        else:
            recordType = "Misc"

        #Make sure fileID is not a tuple
        if isinstance(fileID, tuple):
            fileID = fileID[0]
        #Create file records for the slideshow project files
        c.execute("SELECT * FROM FileRecord WHERE file_id = ? AND slideshow_id = ?", (fileID, slideshowID))
        fileRecords = c.fetchone()
        if fileRecords == None:
            #We need to insert the file record into the database.
            c.execute("INSERT INTO FileRecord (file_id, slideshow_id, FileName, RecordType) VALUES (?, ?, ?, ?)", (fileID, slideshowID, os.path.basename(file), recordType))
        else:
            #There already exists a file record so who gives a shit.
            pass

    #Insert slides into the database
    print("\nInserting slides into the database...")
    for slide in slideList:
        print(f"Slide: {slide}")
        slideOrder = slide.slideID
        transition = slide.transition
        transitionSpeed = slide.transitionSpeed
        slideDuration = slide.duration

        #Get the fileID from the file with the same path as the slide
        c.execute("SELECT id FROM File WHERE file_path = ?", (slide.imagePath,))
        fileID = c.fetchone()[0]
        #This has to exist because earlier you litteraly dump every image and song into the database.

        slideID = slide.slideDB_ID
        #Check if the slide is actually in the database
        c.execute("SELECT id FROM Slide WHERE id = ? AND Slideshow_ID = ?", (slideID,slideshowID))
        result = c.fetchone()
        if result == None:
            slideID = None


        if slideID == None:
            #Slide is not in the database so we need to insert it.
            c.execute('''INSERT INTO Slide
                      (slide_order, transition, transition_speed, slide_duration, SlideRecord_id, Slideshow_ID) VALUES (?, ?, ?, ?, ?, ?)''',
                      (slideOrder, transition, transitionSpeed, slideDuration, fileID, slideshowID))
            #Get the slide id of the slide that matches what was just inserted
            c.execute("SELECT id FROM Slide WHERE slide_order = ? AND Slideshow_ID = ?", (slideOrder, slideshowID))
            slideID = c.fetchone()[0]
            #Update the slideList with the new slideID
            slideList[slideList.index(slide)].slideDB_ID = slideID
            slide.slideDB_ID = slideID
            print(f"New slide ID: {slideID}")
        else:
            #Slide is already in the database so we need to update it.
            c.execute('''UPDATE Slide
                      SET slide_order = ?, transition = ?, transition_speed = ?, slide_duration = ?, SlideRecord_id = ?, Slideshow_ID = ? WHERE id = ?''',
                      (slideOrder, transition, transitionSpeed, slideDuration, fileID, slideshowID, slideID))
            print(f"Updating slide: {slideID}")
            

    #Number of slides in the slideshow
    slideCount = len(slideList)
    #Get the slides that are in the database but not in the slideshow and delete them.
    c.execute("SELECT id FROM Slide WHERE Slideshow_ID = ?", (slideshowID,))
    slidesInDB = c.fetchall()
    slidesInDB = [slide[0] for slide in slidesInDB]
    for slide in slidesInDB:
        if slide not in [slide.slideDB_ID for slide in slideList]:
            c.execute("DELETE FROM Slide WHERE id = ?", (slide,))
            print(f"Deleting slide: {slide}")

    #Insert songs into the database
    print("\nInserting songs into the database...")
    for song in playlist.songs:
        # print(f"Song: {song}")
        songName = song.name
        songOrder = playlist.songs.index(song)
        duration = song.duration
        fileType = song.fileType

        #Get the fileID from the file with the same path as the song
        c.execute("SELECT id FROM File WHERE file_path = ?", (song.filePath,))
        fileID = c.fetchone()[0]

        songID = song.songDB_ID
        #Check if the song is actually in the database
        c.execute("SELECT id FROM Song WHERE id = ? AND Slideshow_ID = ?", (songID, slideshowID))
        result = c.fetchone()
        if result == None:
            songID = None

        if songID == None:
            #Song is not in the database so we need to insert it.
            c.execute('''INSERT INTO Song
                      (song_order, SongRecord_id, duration, filetype, song_name, Slideshow_ID) VALUES (?, ?, ?, ?, ?, ?)''',
                      (songOrder, fileID, duration, fileType, songName, slideshowID))
            #Get the song id of the song that matches what was just inserted
            c.execute("SELECT id FROM Song WHERE song_order = ? AND Slideshow_ID = ?", (songOrder, slideshowID))
            songID = c.fetchone()[0]
            #Update the song with the new songID
            playlist.songs[playlist.songs.index(song)].songDB_ID = songID
            song.songDB_ID = songID
            print(f"New song ID: {songID}")
        else:
            #Song is already in the database so we need to update it.
            c.execute('''UPDATE Song
                      SET song_order = ?, SongRecord_id = ?, duration = ?, filetype = ?, song_name = ?, Slideshow_ID = ? WHERE id = ?''',
                      (songOrder, fileID, duration, fileType, songName, slideshowID, songID))
            print(f"Updating song: {songID}")


    #Number of songs in the playlist
    songCount = len(playlist.songs)
    #Get the songs that are in the database but not in the playlist and delete them.
    c.execute("SELECT id FROM Song WHERE Slideshow_ID = ?", (slideshowID,))
    songsInDB = c.fetchall()
    songsInDB = [song[0] for song in songsInDB]
    for song in songsInDB:
        if song not in [song.songDB_ID for song in playlist.songs]:
            c.execute("DELETE FROM Song WHERE id = ?", (song,))
            print(f"Deleting song: {song}")


    #remove tags that are just whitespace
    tags = [tag for tag in tags if tag.strip() != ""]

    #Insert tags into the database
    print("\nInserting tags into the database...")
    #First delete all TagRecords for this specific slideshow
    c.execute("DELETE FROM TagRecord WHERE slideshow_id = ?", (slideshowID,))
    # print(f"TagRecords for slideshow: {slideshowID} deleted")
    print(f"Tags: {tags}")
    for tag in tags:
        # print(f"Inserting tag: {tag}")
        #Check if the tag is already in the database
        c.execute("SELECT tag_id FROM Tags WHERE tag_name = ?", (tag,))
        tag_id = c.fetchone()
        if tag_id == None:
            #If there is no tag_id its a brand new tag so we need to insert it.
            c.execute("INSERT INTO Tags (tag_name) VALUES (?)", (tag,))
            #Get the tag id of the tag that matches what was just inserted
            c.execute("SELECT tag_id FROM Tags WHERE tag_name = ?", (tag,))
            tag_id = c.fetchone()[0]
        else:
            #Tag is already in the database so we don't need to worry about it.
            tag_id = tag_id[0]

        #clean the tag_id
        if isinstance(tag_id, tuple):
            tag_id = tag_id[0]

        #Insert the tag record into the database
        c.execute("INSERT INTO TagRecord (tag_id, slideshow_id) VALUES (?, ?)", (tag_id, slideshowID))


    conn.commit()
    conn.close()

    print("\nSlideshow saved to the database.")
    if toFile:
        print(f"Saving to file: {saveLocation}")
        tempSaveLocation = slideshow.getSaveLocation()
        slideshow.setSaveLocation(saveLocation)
        slideshow.save()
        slideshow.setSaveLocation(tempSaveLocation)

    validateDatabase()

    return True

def getSlideshows():
    print("\nGetting slideshows from the database...")
    print("Slideshows in the database:")
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()

    c.execute("SELECT * FROM Slideshows")
    slideshows = c.fetchall()
    conn.close()
    #Put them into a dictionary
    sd = {}
    for slideshow in slideshows:
        s = {
            "slideshowID": slideshow[0],
            "slideshowName": slideshow[1],
            "lastModified": slideshow[7],
            "tags": slideshow[8]
        }
        sd[slideshow[0]] = s
    
    # pprint.pprint(sd)
    return sd

def checkSlideshowExists(slideshowID):
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()
    c.execute("SELECT slideshow_ID FROM Slideshows WHERE slideshow_ID = ?", (slideshowID,))
    result = c.fetchone()
    conn.close()
    if result == None:
        return False
    return True

def loadSlideshow(slideshowID) -> FP.Slideshow:
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()

    #Get the slideshow information
    c.execute("SELECT * FROM Slideshows WHERE slideshow_ID = ?", (slideshowID,))
    slideshow = c.fetchone()
    if slideshow == None:
        print("Slideshow not found")
        return None
    
    slideshowID = slideshow[0]
    slideshowName = slideshow[1]
    loopSetting = slideshow[2]
    manualControls = bool(slideshow[3])
    slideShuffle = bool(slideshow[4])
    playlistShuffle = bool(slideshow[5])
    playlistDuration = slideshow[6]
    lastModified = slideshow[7]

    #Get the tags for the slideshow
    tags = getTags(slideshowID)

    #Get files in the project
    c.execute("SELECT file_id FROM FileRecord WHERE slideshow_id = ?", (slideshowID,))
    fileRecords = c.fetchall()
    fileRecords = [fileRecord[0] for fileRecord in fileRecords]

    #Get every file in the database
    c.execute("SELECT id, file_path FROM File")
    files = c.fetchall()
    files = {file[0]:file[1] for file in files}

    #Get every file in the project
    filesInProject = []
    for fileRecord in fileRecords:
        filesInProject.append(files[fileRecord])

    
    #Get the songfiles in the project which are files that end in .mp3, .wav, .flac, .ogg, .aiff
    songFiles = [file for file in filesInProject if file.endswith((".mp3", ".wav", ".flac", ".ogg", ".aiff"))]

    songList = []
    for song in songFiles:
        #Create a song object
        s = FP.Song(song)
        #add the song to the songList
        songList.append(s)

    #Get the slides in the project
    c.execute("SELECT * FROM Slide WHERE Slideshow_ID = ?", (slideshowID,))
    slides = c.fetchall()

    conn.close()
    
    slideList = []
    for slide in slides:
        slideDB_ID = slide[0]
        slideOrder = slide[1]
        transition = slide[2]
        transitionSpeed = slide[3]
        slideDuration = slide[4]
        slideRecordID = slide[5]
        imagePath = files[slideRecordID]
        slide = FP.Slide(imagePath)
        slide.slideDB_ID = slideDB_ID
        slide.slideID = slideOrder
        slide.transition = transition
        slide.transitionSpeed = transitionSpeed
        slide.duration = slideDuration
        slideList.append(slide)

    #Create a playlist object
    playlist = FP.Playlist()
    playlist.shuffle = playlistShuffle
    #Add the songs
    playlist.songs = songList
    playlist.validate()

    #Create a slideshow object
    slideshow = FP.Slideshow(slideshowName)
    slideshow.name = slideshowName
    slideshow.slides = slideList
    slideshow.getSlideCount() #Sets the slidecount to len(slides)
    slideshow.playlist = playlist
    slideshow.loopSettings = loopSetting
    slideshow.manual = manualControls
    slideshow.shuffle = slideShuffle
    #Get the files that end with an image extension
    imageFiles = [file for file in filesInProject if file.endswith((".png", ".jpg", ".jpeg"))]
    slideshow.filesInProject = imageFiles
    slideshow.slideshowID = slideshowID
    slideshow.tags = tags
    slideshow.setSaveLocation("Saved To Database")

    # print(slideshow)
    return slideshow


def deleteSlideshow(slideshowID):
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()

    #Delete the slideshow
    c.execute("DELETE FROM Slideshows WHERE slideshow_ID = ?", (slideshowID,))
    #Delete the slides
    c.execute("DELETE FROM Slide WHERE Slideshow_ID = ?", (slideshowID,))
    #Delete the songs
    c.execute("DELETE FROM Song WHERE Slideshow_ID = ?", (slideshowID,))
    #Delete the file records
    c.execute("DELETE FROM FileRecord WHERE slideshow_id = ?", (slideshowID,))
    #Delete the tag records
    c.execute("DELETE FROM TagRecord WHERE slideshow_id = ?", (slideshowID,))
    
    conn.commit()
    conn.close()

def validateDatabase():
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()
    #Get a list of all slideshowIDs in the database
    c.execute("SELECT slideshow_ID FROM Slideshows")
    real_slideshowIDs = c.fetchall()
    real_slideshowIDs = [slideshowID[0] for slideshowID in real_slideshowIDs]

    #Get a list of all slideshowIDs in the database
    c.execute("SELECT Slideshow_ID FROM Slide")
    slide_slideshowIDs = c.fetchall()
    slide_slideshowIDs = [slideshowID[0] for slideshowID in slide_slideshowIDs]

    #Get a list of all slideshowIDs in the database
    c.execute("SELECT Slideshow_ID FROM Song")
    song_slideshowIDs = c.fetchall()
    song_slideshowIDs = [slideshowID[0] for slideshowID in song_slideshowIDs]

    #combine both lists
    possible_slideshowIDs = slide_slideshowIDs + song_slideshowIDs
    possible_slideshowIDs = [int(slideshowID) for slideshowID in possible_slideshowIDs]
    
    #If a possible_slideshowID is not in real_slideshowIDs then elements related to that slideshow are not being used and should be deleted.
    for slideshowID in real_slideshowIDs:
        if slideshowID not in possible_slideshowIDs:
            print(f"Deleting dead slideshow: {slideshowID}")
            deleteSlideshow(slideshowID)

    conn.commit()
    #Delete unused files

    #Get a list of all fileIDs in the database
    c.execute("SELECT id FROM File")
    real_fileIDs = c.fetchall()
    real_fileIDs = [fileID[0] for fileID in real_fileIDs]

    #Get a list of all fileIDs in FileRecords in the database
    c.execute("SELECT file_id FROM FileRecord")
    fileRecord_fileIDs = c.fetchall()
    fileRecord_fileIDs = [fileID[0] for fileID in fileRecord_fileIDs]

    #If a file does not have a record, then it isn't being used and it should be deleted.
    for fileID in real_fileIDs:
        if fileID not in fileRecord_fileIDs:
            print(f"Deleting unused file: {fileID}")
            c.execute("DELETE FROM File WHERE id = ?", (fileID,))

    conn.commit()


    #Get all tags_ids from tagRecord
    c.execute("SELECT tag_id FROM TagRecord")
    tags_In_Use = c.fetchall()
    tags_In_Use = [tag[0] for tag in tags_In_Use]
    # print(f"Tags in use: {tags_In_Use}")

    #Get all tags in the database
    c.execute("SELECT tag_id FROM Tags")
    all_tags = c.fetchall()
    all_tags = [tag[0] for tag in all_tags]
    # print(f"All tags: {all_tags}")

    #If there is a tag without a record, then it isn't being used and it should be deleted.
    for tag in all_tags:
        if tag not in tags_In_Use:
            print(f"Deleting unused tag: {tag}")
            c.execute("DELETE FROM Tags WHERE tag_id = ?", (tag,))


    conn.commit()

    #Get all the tagRecords
    c.execute("SELECT * FROM TagRecord")
    tagRecords = c.fetchall()
    
    #Get all slideshowIDS and tagIDs
    c.execute("SELECT slideshow_ID FROM Slideshows")
    slideshowIDs = c.fetchall()
    slideshowIDs = [slideshowID[0] for slideshowID in slideshowIDs]

    c.execute("SELECT tag_id FROM Tags")
    tagIDs = c.fetchall()
    tagIDs = [tagID[0] for tagID in tagIDs]

    #If a tagRecord has a slideshowID or tagID that doesn't exist, then it should be deleted.
    for tagRecord in tagRecords:
        id = tagRecord[0]
        tag_id = tagRecord[1]
        slideshow_id = tagRecord[2]
        if tag_id not in tagIDs or slideshow_id not in slideshowIDs:
            print(f"Deleting tagRecord: {id}")
            c.execute("DELETE FROM TagRecord WHERE id = ?", (id,))



    conn.commit()
    conn.close()

def sqlProtector(string):
    if string == None:
        return False
    #Parse the string
    try:
        parsed = sqlparse.parse(string)
    except:
        return False
    if len(parsed) > 1:
        print(f"Injections detected. attempt={string}")
        return True
    else:
        return False
    
def addTag(tag:str, slideshowID:int):
    print(f"\nAdding tag: {tag} to the database...")
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()

    if sqlProtector(tag):
        print("Injection detected")
        return False

    #Check if the tag is already in the database
    c.execute("SELECT tag_id FROM Tags WHERE tag_name = ?", (tag,))
    tag_id = c.fetchone()
    if tag_id == None:
        #We need to insert the tag into the database.
        c.execute("INSERT INTO Tags (tag_name) VALUES (?)", (tag,))
        #Get the tag id of the tag that matches what was just inserted
        c.execute("SELECT tag_id FROM Tags WHERE tag_name = ?", (tag,))
        tag_id = c.fetchone()[0]
        conn.commit()
    else:
        #Tag is already in the database so we don't need to worry about it.
        print("Tag already in the database")
        tag_id = tag_id[0]

    #clean the tag_id
    if isinstance(tag_id, tuple):
        tag_id = tag_id[0]

    #Insert the tag record into the database
    c.execute("INSERT INTO TagRecord (tag_id, slideshow_id) VALUES (?, ?)", (tag_id, slideshowID))
    conn.commit()
    conn.close()
    return True
    
def removeTag(tag:str, slideshowID:int):
    print(f"\nRemoving tag: {tag} from Slideshow: {slideshowID}...")
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()

    if sqlProtector(tag):
        print("Injection detected")
        conn.close()
        return False
    
    #Remove the tagrecord from the database
    c.execute("SELECT id FROM TagRecord WHERE tag_id = ? AND slideshow_id = ?", (tag, slideshowID))
    tagRecord = c.fetchone()
    if tagRecord != None:
        c.execute("DELETE FROM TagRecord WHERE id = ?", (tagRecord[0],))
        conn.commit()
        conn.close()
        return True
    else:
        print("Tag not found")
        conn.commit()
        conn.close()
        return False
    

def getTags(slideshowID):
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()

    #Get the tags for the slideshow
    c.execute("SELECT tag_id FROM TagRecord WHERE slideshow_id = ?", (slideshowID,))
    tag_ids = c.fetchall()
    tag_ids = [tag_id[0] for tag_id in tag_ids]

    tags = []
    for tag_id in tag_ids:
        c.execute("SELECT tag_name FROM Tags WHERE tag_id = ?", (tag_id,))
        tag = c.fetchone()[0]
        tags.append(tag)
    
    conn.commit()
    conn.close()
    return tags

def getAllTags():
    conn = sqlite3.connect(databasePath)
    c = conn.cursor()

    #Get the tags for the slideshow
    c.execute("SELECT tag_name FROM Tags")
    tags = c.fetchall()
    tags = [tag[0] for tag in tags]
    
    conn.commit()
    conn.close()
    return tags


createDatabase()
validateDatabase()

resetDatabase()
saveSlideshow(r"C:\Users\JamesH\OneDrive - uah.edu\CS499\TestImages3\Kitty.pyslide")
saveSlideshow(r"C:\Users\JamesH\OneDrive - uah.edu\CS499\OneSlide.pyslide")
saveSlideshow(r"C:\Users\JamesH\OneDrive - uah.edu\CS499\exported_assets_test1_2024-04-09_20-45-57\test1.pyslide")
saveSlideshow(r"C:\Users\JamesH\OneDrive - uah.edu\CS499\exported_assets_test1_2024-04-09_20-45-57\test1.pyslide")
renameSlideshow(1, "Test1")
saveSlideshow(r"C:\Users\JamesH\OneDrive - uah.edu\CS499\OneSlide.pyslide")
saveSlideshow(r"C:\Users\JamesH\OneDrive - uah.edu\CS499\TestImages3\Kitty.pyslide")


# Latop
# saveSlideshow(r"C:\Users\flami\OneDrive - uah.edu\CS499\OneSlide.pyslide")
# saveSlideshow(r"C:\Users\flami\OneDrive - uah.edu\CS499\TestImages3\Kitty.pyslide")
# saveSlideshow(r"C:\Users\flami\OneDrive - uah.edu\CS499\exported_assets_test1_2024-04-09_20-45-57\test1.pyslide")

# deleteSlideshow(1)

# clearDatabase()