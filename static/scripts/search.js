//EVENT LISTENER to send the request
document.getElementById('search').addEventListener('click', function() {
    // Check if 2 dates are chosen AND if there is a departing + returning date
    if( document.getElementById('firstname').value.length && 
        document.getElementById('lastname').value.length &&
        chosenDates.length == 2) {      
            
        //TEST Display dates chosen    
        console.log("CHOSEN DATES: ")
        for(const chosenDate of chosenDates) {
          console.log("-" + chosenDate)
        }

        //Hide the form and calendar, and display loading animation
        document.getElementById('loading').style.display = 'flex';
        document.getElementById('form').style.display = 'none';
        document.getElementById('calendar').style.display = 'none';
    }

    if(false) {
        var xhr = new XMLHttpRequest();
        // we defined the xhr

        xhr.onreadystatechange = function () {
            if (this.readyState != 4) return;

            if (this.status == 200) {
                var responseHTML = this.responseText;
                console.log(responseHTML)
                document.open();
                document.write(responseHTML);
                document.close();
            }

            // end of state change: it can be after some time (async)
        };

        xhr.open('POST', '/returnDates', true);
        xhr.setRequestHeader('Content-Type', 'application/json');

        const data = {dates: datesToSearch, names: datesNames}

        xhr.send(JSON.stringify(data));
    } 

})