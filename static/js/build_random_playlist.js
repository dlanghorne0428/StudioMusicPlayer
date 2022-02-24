// this is the part of the form where user enters percentages for each dance style
const pct_div = document.getElementById("enter-percentages");

// get a list of all input elements in that part of the form
const pct_inputs = pct_div.getElementsByTagName("input");

// add event listener for clicks on any of those input elements to 
for(var i = 0; i < pct_inputs.length; i++) {
    pct_inputs[i].addEventListener('click', myFunction);
};

function myFunction() {
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