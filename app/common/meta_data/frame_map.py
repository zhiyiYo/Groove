# refer to: https://picard-docs.musicbrainz.org/en/appendices/tag_mapping.html

ID3_FRAME_MAP = {
    "title": "TIT2",
    "singer": "TPE1",
    "album": "TALB",
    "year": "TDRC",
    "genre": "TCON",
    "track": "TRCK",
    "disc": "TPOS",
    "trackTotal": "TRCK",
    "discTotal": "TPOS",
    "lyrics": "USLT"
}


MP4_FRAME_MAP = {
    "title": "©nam",
    "singer": ["©ART", "aART"],
    "album": "©alb",
    "year": "©day",
    "genre": "©gen",
    "track": "trkn",
    "disc": "disk",
    "trackTotal": "trkn",
    "discTotal": "disk",
    "lyrics": "©lyr"
}


VORBIS_FRAME_MAP = {
    "title": "title",
    "singer": "artist",
    "album": "album",
    "year": ["date", "year"],
    "genre": "genre",
    "track": "tracknumber",
    "disc": "discnumber",
    "trackTotal": "tracktotal",
    "discTotal": "discTotal",
    "lyrics": "lyrics"
}


APEV2_FRAME_MAP = {
    "title": "Title",
    "singer": "Artist",
    "album": "Album",
    "year": "Year",
    "genre": "Genre",
    "track": "Track",
    "disc": "Disc",
    "trackTotal": "Track",
    "discTotal": "Disc",
    "lyrics": "Lyrics"
}


ASF_FRAME_MAP = {
    "title": "Title",
    "singer": "Author",
    "album": "WM/AlbumTitle",
    "year": "WM/Year",
    "genre": "WM/Genre",
    "track": "WM/TrackNumber",
    "disc": "WM/PartOfSet",
    "trackTotal": "WM/TrackNumber",
    "discTotal": "WM/PartOfSet",
    "lyrics": "WM/Lyrics"
}
