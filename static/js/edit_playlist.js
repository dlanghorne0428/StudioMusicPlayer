//get form
const playlist_info_form = document.getElementById("id-PlaylistEditForm");

// get form fields
const title = document.getElementById("id_title");
const max_duration = document.getElementById("id_max_song_duration");
const auto_continue = document.getElementById("id_auto_continue");
const description = document.getElementById("id_description");

// get a list of all input elements in that part of the form
const playlist_songs = document.getElementById("playlist-songs");

// add event listener for mousedown on any songs in the playlist
playlist_songs.addEventListener('mousedown', mySelectFunction);

// get hidden element for drawing a song note during drag-and-drop
const songNoteIcon = document.getElementById('song-note-icon');

// add event listener for changes to the selection on any of the form fields
title.addEventListener('change', mySubmitFunction);
max_duration.addEventListener('change', mySubmitFunction);
auto_continue.addEventListener('change', mySubmitFunction);
description.addEventListener('change', mySubmitFunction);

// submit the form when any of the events happen
function mySubmitFunction() {
    playlist_info_form.submit();
};

var songIndex;
var newSongIndex;
var selectedElement;
var currentElement;


function table_index(table_row_element) {
    return parseInt(table_row_element.firstElementChild.innerHTML ) - 1;
};


function adjustBorder(elemBelow) {
    elemBelow.style.borderTop = "3px solid red";
    currentElement.style.borderTop = "1px solid";
    currentElement = elemBelow;
};


function moveAt(event) {
    var latestIndex;
    songNoteIcon.style.left = event.pageX - songNoteIcon.offsetWidth / 2 + 'px';
    songNoteIcon.style.top = event.pageY - songNoteIcon.offsetHeight / 2 + 'px';
    songNoteIcon.hidden = true;
    var elemBelow = document.elementFromPoint(event.clientX, event.clientY);
    console.log(elemBelow.innerHTML);
    do {
        elemBelow = elemBelow.parentElement;
    } while (elemBelow.tagName != "TR");
    latestIndex = table_index(elemBelow);
    if (latestIndex != newSongIndex) {   
        newSongIndex = latestIndex;
        adjustBorder(elemBelow);
        console.log("Moving:", songNoteIcon.style.left, songNoteIcon.style.top,  "Index: ", newSongIndex);
    }
    songNoteIcon.hidden = false;
};


// select table row for drag
function mySelectFunction(event) {
    console.log('Down coordinates: ', event.pageX, event.pageY);
    selectedElement = event.target;
    do {
        selectedElement = selectedElement.parentElement;
    } while (selectedElement.tagName != "TR");
    selectedElement.style.backgroundColor = 'lightGray';
    songIndex = table_index(selectedElement);
    console.log(songIndex);
    currentElement = selectedElement;
    newSongIndex = songIndex;
    songNoteIcon.removeAttribute("hidden");
    songNoteIcon.ondragstart = function () {
        return false;
    };
    moveAt(event);
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', myReleaseFunction);
};

function onMouseMove(event) {
    moveAt(event);
};

// Drop
function myReleaseFunction(event) {
    console.log('Up coordinates: ', event.pageX, event.pageY);
    selectedElement.style.backgroundColor = 'white';
    songNoteIcon.setAttribute('hidden', '');
    document.removeEventListener('mousemove', onMouseMove);
    if (newSongIndex != songIndex) { 
        console.log("Selected Index: ", songIndex, "New Index: ", newSongIndex);
        var myUrl = new URL(window.location.href);
        myUrl.searchParams.append("cmd", "dragsong");
        myUrl.searchParams.append("index", songIndex);
        myUrl.searchParams.append('newIndex', newSongIndex);
        console.log(myUrl);
        
        theLink = document.getElementById('submit-drag-drop-song');
        theLink.setAttribute('href', myUrl);
        theLink.click();
    };
};
