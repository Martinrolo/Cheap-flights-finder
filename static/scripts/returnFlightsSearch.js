let nbSelected = 0;
let datesToSearch = [];
let datesNames = []

document.querySelectorAll('tr').forEach(function(tr) {
    tr.addEventListener('click', function() {
        if(tr.classList.contains('selected')) {
            //Remove the class, decrement nbSelected and remove the date from the array
            tr.classList.remove('selected')
            nbSelected--;
            let indexToRemove = datesToSearch.indexOf(tr.id);
            datesToSearch.splice(indexToRemove, 1)
            datesNames.splice(indexToRemove, 1)
        }

        else if(nbSelected < 3) {
            //Add the class, increment nbSelected and add the date to the array
            tr.classList.add('selected');
            nbSelected++;
            datesToSearch.push(tr.id)
            
            datesNames.push(tr.children[0].children[0].innerText)
            console.log("NAME PUSHED: " + datesNames[0])
        }

        //TEST
        console.log("DATES: ")
        datesToSearch.forEach(function(date) {
            console.log(date)
        })
    })
})

//FUNCTION LOADING
function loading(){
    //Only hide them if there is a search to make
    if (nbSelected > 0) {
        document.getElementById('loading').style.display = 'flex';
        document.getElementById('content').style.display = 'none';
    }
}

//EVENT LISTENER to send the request
document.getElementById('search').addEventListener('click', function() {
    //If at least 1 element is selected
    if (nbSelected > 0) {
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