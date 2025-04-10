var error_counter = 0;
function validateExamForm(type){
    
    event.preventDefault();
    $('#output_course').empty()
    error_counter = 0;
    if (document.getElementById("university").value == ''){
        displayError("university", "Please select a University")
    }
    if (document.getElementById("course").value == ''){
        displayError("course", "Please select a Course")
    }
    if (document.getElementById("Stream").value == ''){
        displayError("Stream", "Please select a Stream")
    }
    if (document.getElementById("studypattern").value == ''){
        displayError("studypattern", "Please select a Study Pattern")
    }
    if (document.getElementById("semyear").value == ''){
        displayError("semyear", "Please select valid Semester/Year")
    }
    if (type === "Submit"){
        if (document.getElementById("exam_date").value == ''){
            displayError("exam_date", "Please enter a valid Exam Date")
        }
        if (document.getElementById("exam_time").value == ''){
            displayError("exam_time", "Please enter a valid Exam Start Time")
        }
        if (document.getElementById("exam_end_time").value == ''){
            displayError("exam_end_time", "Please enter a valid Exam End Time")
        }
        if (document.getElementById("exam_duration").value == ''){
            displayError("exam_duration", "Please enter a valid Exam Duration")
        }
        if (document.getElementById("exam_name").value == ''){
            displayError("exam_name", "Please enter a valid Exam Name")
        }
        if (document.getElementById("total_marks").value == ''){
            displayError("total_marks", "Please enter Total Marks")
        }
        var uploadFileInput = $('#upload_file')[0].files;
        if (uploadFileInput.length === 0) {
            displayError("upload_file", "Please upload a file");
        }
        startTime = document.getElementById('exam_time').value;
        endTime = document.getElementById('exam_end_time').value;
       
        var start = new Date("1970-01-01T" + startTime + ":00Z");
        var end = new Date("1970-01-01T" + endTime + ":00Z");
        
    // Compare the two times
        if (start >= end) {
            displayError("exam_time", "Start time cannot be greater than end time");
            

        }
    }
    if (error_counter == 0){
        return true;
    }
    else{
        $('#exampleModal').modal('show');
    }
    



}

function displayError(name, message){
    console.error(name, message);
    document.getElementById(name).focus();
    document.getElementById(name).classList.add('error')
    //alert(message)
    //return false;
   
    error_counter++;

    $('#output_course').append(`
        <p class=" text-darkblue font-14" > ${message} </p>
      `);
}