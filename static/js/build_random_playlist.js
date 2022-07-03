// this is the part of the form where user enters the total number of songs in the playlist
const total_songs_div = document.getElementById("div_id_number_of_songs");

// get a list of all input elements in that part of the form
const total_song_inputs = total_songs_div.getElementsByTagName("input");
console.log(total_song_inputs[0].value);

// this is the part of the form where user enters number of songs for each dance style
const count_div = document.getElementById("enter-songs-per-dance-style");

// get a list of all input elements in that part of the form
const count_inputs = count_div.getElementsByTagName("input");

// add event listener for clicks on any of the song count input elements
for(var i = 0; i < count_inputs.length; i++) {
    count_inputs[i].addEventListener('click', myTotalFunction);
};

// this is the part of the form where user selects holiday themed songs
const holi_div = document.getElementById("enter-holidays");

// get a list of all select elements in the holiday part of the form
const holi_selects = holi_div.getElementsByTagName("select");

// add event listener for changes the selection on any of the holiday input elements
for(var i = 0; i < holi_selects.length; i++) {
    holi_selects[i].addEventListener('change', myFocusFunction);
};

function myTotalFunction() {
    // get the elements we need to alter
    const continue_button = document.getElementById("submit-id-continue");
    const error_text = document.getElementById("count-error");
    const error_total = document.getElementById("count-total");
    
    // add up the song counts of the input elements
    var count_total = 0;
    for(var i = 0; i < count_inputs.length; i++) {
        count_total += Number(count_inputs[i].value);
    };
    
    if (count_total == Number(total_song_inputs[0].value)) {
        // enable the continue button and hide the errors
        continue_button.removeAttribute('disabled');
        error_text.setAttribute('hidden', '');      
    } else {
        // bad total, disable continue button, show error with current total 
        continue_button.setAttribute('disabled', '');
        error_text.removeAttribute('hidden');
        error_total.innerHTML=count_total
    };
};

function myFocusFunction() {
    // get the holiday element that was changed
    var e = event.target;
    // if the new value is every other, every third, or every fourth song
    if (e.value.slice(0, 2) == "Ev") {
        // set the selection of all other holidays to Exclude
        for (var index = 0; index < holi_selects.length; index++) {
            if (holi_selects[index] != e) {
                holi_selects[index].value = "Ex";
            }
        };
        // no need to look at other holidays once we find one that is focused
        return;
    };
};


myTotalFunction();

// trigger the tooltips for elements with data-bs-toggle attribute set
// see: https://getbootstrap.com/docs/5.0/components/tooltips/
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})