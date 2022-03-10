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