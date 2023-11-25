//get form
const song_filter_form = document.getElementById("song-filter-form");

// get form fields
const artist = document.getElementById("artist-filter");
const title = document.getElementById("title-filter");
const dance_type = document.getElementById("dance-type-filter");

// add event listener for changes to the selection on any of the form fields
artist.addEventListener('change', mySubmitFunction);
title.addEventListener('change', mySubmitFunction);
dance_type.addEventListener('change', mySubmitFunction);

// submit the form when any of the events happen
function mySubmitFunction() {
    song_filter_form.submit();
};