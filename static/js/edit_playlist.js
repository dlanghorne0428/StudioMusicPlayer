///////////////////////////////////
// form code for playlist metadata
///////////////////////////////////

//get form
const playlist_info_form = document.getElementById("id-PlaylistEditForm");

// get form fields
const title = document.getElementById("id_title");
const max_duration = document.getElementById("id_max_song_duration");
const auto_continue = document.getElementById("id_auto_continue");
const description = document.getElementById("id_description");

// add event listener for changes to the selection on any of the form fields
title.addEventListener('change', mySubmitFunction);
max_duration.addEventListener('change', mySubmitFunction);
auto_continue.addEventListener('change', mySubmitFunction);
description.addEventListener('change', mySubmitFunction);

// submit the form when any of the events happen
function mySubmitFunction() {
    playlist_info_form.submit();
};


/////////////////////////////////////////////////////////////////////////////////////////////
// Drag and Drop code                                                                      //
// Inspired by: https://www.w3docs.com/learn-javascript/drag-and-drop-with-javascript.html //
/////////////////////////////////////////////////////////////////////////////////////////////

// get the table body element that holds the playlist songs
const playlist_songs = document.getElementById("playlist-song-table-body");

// add event listener for mousedown on the playlist table body
playlist_songs.addEventListener('mousedown', mySelectFunction);

// get hidden element for drawing a song note during drag-and-drop
const songNoteIcon = document.getElementById('song-note-icon');

// variables for table indices
var songIndex;
var newSongIndex;

// variables for HTML elements 
var selectedElement;
var currentElement;


// find the song order in the playlist, based on the table row element
function table_index(table_row_element) {
    // the first column in the table is a one-based index, subtract one for the playlist order
    return parseInt(table_row_element.firstElementChild.innerHTML ) - 1;
};


// change the borders of table elements
function adjustBorder(elemBelow) {
    // top border of the selected element is highlighted to indicate the drop target
    elemBelow.style.borderTop = "3px solid red";
    //reset the top border of the previously selected element to normal style
    currentElement.style.borderTop = "1px solid";
    // remember the currently selected element as the drop target
    currentElement = elemBelow;
};


// handle mouse move event
function moveAt(event) {
    var latestIndex;
    // move the icon so it is centered under the mouse pointer
    songNoteIcon.style.left = event.pageX - songNoteIcon.offsetWidth / 2 + 'px';
    songNoteIcon.style.top = event.pageY - songNoteIcon.offsetHeight / 2 + 'px';
    
    // find the HTML element below the icon, hide the icon temporarily to access it
    songNoteIcon.hidden = true;
    var elemBelow = document.elementFromPoint(event.clientX, event.clientY);
    //console.log(elemBelow.innerHTML);
    // TODO: check for null, also need to handle the bottom of the table.
    // traverse the parent element until you get to the table row and find the song index
    do {
        elemBelow = elemBelow.parentElement;
    } while (elemBelow.tagName != "TR");
    latestIndex = table_index(elemBelow);
    
    // if the index has changed, update the newSongIndex and update the border
    if (latestIndex != newSongIndex) {   
        newSongIndex = latestIndex;
        adjustBorder(elemBelow);
        console.log("Moving:", songNoteIcon.style.left, songNoteIcon.style.top,  "Index: ", newSongIndex);
    }
    // unhide the icon to keep dragging
    songNoteIcon.hidden = false;
};


// select table row for drag
function mySelectFunction(event) {
    // get the selected element
    selectedElement = event.target;
    
    // if selected element is not a standard table data element, return. 
    // this allows anchor elements and buttons to handle click events
    if (selectedElement.tagName != "TD") {
        return;
    }
    
    // traverse parent elements until you get to the table row
    do {
        selectedElement = selectedElement.parentElement;
    } while (selectedElement.tagName != "TR");
    console.log('Down coordinates: ', event.pageX, event.pageY);
    
    // highlight selected element and find the song index in the playlist
    selectedElement.style.backgroundColor = 'lightGray';
    songIndex = table_index(selectedElement);
    console.log(songIndex);
    
    // initialize the tracking current element and new song index 
    currentElement = selectedElement;
    newSongIndex = songIndex;
    
    // unhide the songNoteIcon and prevent the standard dragging behavior
    songNoteIcon.removeAttribute("hidden");
    songNoteIcon.ondragstart = function () {
        return false;
    };
    
    // call mousemove event handling and listen for other mouse moves and mouse up events
    moveAt(event);
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', myReleaseFunction);
};


// call existing function to handle mouse move events
function onMouseMove(event) {
    moveAt(event);
};


// Handle mouse up for drop
function myReleaseFunction(event) {
    console.log('Up coordinates: ', event.pageX, event.pageY);
    // clear highlighting of original selection and hide the note icon
    selectedElement.style.backgroundColor = 'white';
    songNoteIcon.setAttribute('hidden', '');
    
    // quit listening for mouse moves
    document.removeEventListener('mousemove', onMouseMove);
    
    // if new index is different from the original selection
    if (newSongIndex != songIndex) { 
        console.log("Selected Index: ", songIndex, "New Index: ", newSongIndex);
        
        // build URL from current, add command and indices as search parameters
        var myUrl = new URL(window.location.href);
        myUrl.searchParams.append("cmd", "dragsong");
        myUrl.searchParams.append("index", songIndex);
        myUrl.searchParams.append('newIndex', newSongIndex);
        console.log(myUrl);
        
        // find the hidden link element for this URL and perform a click event to process the drag/drop
        theLink = document.getElementById('submit-drag-drop-song');
        theLink.setAttribute('href', myUrl);
        theLink.click();
    };
};
