// this is the part of the form where user enters percentages for each dance style
const pct_div = document.getElementById("enter-percentages");

// get a list of all input elements in that part of the form
const pct_inputs = pct_div.getElementsByTagName("input");

// add event listener for clicks on any of the percentage input elements
for(var i = 0; i < pct_inputs.length; i++) {
    pct_inputs[i].addEventListener('click', myTotalFunction);
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
    const error_text = document.getElementById("percentage-error");
    const error_total = document.getElementById("percentage-total");
    
    // add up the total percentages of the input elements
    var total = 0;
    for(var i = 0; i < pct_inputs.length; i++) {
        total += Number(pct_inputs[i].value);
    };
    
    if (total == 100) {
        // enable the continue button and hide the errors
        continue_button.removeAttribute('disabled');
        error_text.setAttribute('hidden', '');      
    } else {
        // bad total, disable continue button, show error with current total 
        continue_button.setAttribute('disabled', '');
        error_text.removeAttribute('hidden');
        error_total.innerHTML=total
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