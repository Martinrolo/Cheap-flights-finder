//EVENT LISTENER to send the request
document.getElementById('search').addEventListener('click', function() {
    //Get the input of the user (leavingFrom and goingTo airports)
    let leavingFrom = document.getElementById('firstname').value
    let goingTo = document.getElementById('lastname').value

    // Check if 2 dates are chosen AND if there is a departing + returning date
    if( leavingFrom.length && 
        goingTo.length &&
        chosenDates.length == 2) {   
            
        //SORT the chosen dates array
        if(chosenDates[0] > chosenDates[1]) {
            temp = chosenDates[0];
            chosenDates[0] = chosenDates[1];
            chosenDates[1] = temp
        }
            
        //TEST Display dates chosen    
        console.log("CHOSEN DATES: ")
        for(const chosenDate of chosenDates) {
          console.log("-" + chosenDate)
        }

        //Hide the form and calendar, and display loading animation
        document.getElementById('loading').style.display = 'flex';
        document.getElementById('form').style.display = 'none';
        document.getElementById('calendar').style.display = 'none';

        // ************ HTTP REQUEST ************



        var xhr = new XMLHttpRequest();

        //Request response
        xhr.onreadystatechange = function () {
            if (this.readyState != 4) return;

            if (this.status == 200) {
                var responseHTML = this.responseText;

                //Display the HTML response text
                document.open();
                document.write(responseHTML);
                document.close();
            }
        };

        xhr.open('POST', '/searchDepartingFlights', true);
        xhr.setRequestHeader('Content-Type', 'application/json');

        const data = {leavingFrom: leavingFrom, goingTo: goingTo, dates: chosenDates}

        xhr.send(JSON.stringify(data));
    }
})