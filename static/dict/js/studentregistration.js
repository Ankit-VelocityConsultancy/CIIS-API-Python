var error_counter = 0;
function validateForm(type){
    event.preventDefault();
    $('#output_course').empty()
    error_counter = 0
    if (type !== 'add_others' && type != 'edit_others') {
        if (document.getElementById("university").value == ''){

            displayError("university", "Please select University")
            
        }
    }
    if (type == 'add' || type == 'add_others')  {
        if (document.getElementById("student_image").value == ''){
      
       displayError("imagefile", "Please choose file for student image")
        }
    }
    if (type == 'edit' || type == 'edit_others') {

                if (document.getElementById('uploaded-image').value == 'No files chosen'){
                   
                    displayError('imagefile', 'Please choose file for student image');
                }
            
    }
     if (document.getElementById("name").value == ''){
        displayError("name", "Please enter a Name")
    }
     if (document.getElementById("dateofbirth").value == ''){
        displayError("dateofbirth", "Please enter Birth Date")
    }
    
    if (document.getElementById("fathers_name").value == ''){
       displayError("fathers_name", "Please enter Father's Name")
    }
    if (document.getElementById("mothers_name").value == ''){
        displayError("mothers_name", "Please enter Mother's Name")
    }
     if (document.getElementById("email").value == ''){
        displayError("email", "Please enter Email Address")
    }
     if (document.getElementById("mobile").value == ''){
       displayError("mobile", "Please enter Mobile Number")
    }
     if (document.getElementById("address").value == ''){
        displayError("address", "Please enter Current Address")
    }
     if (document.getElementById("countryId").value == ''){
        displayError("countryId", "Please select Country")
    }
     if (document.getElementById("stateId").value == ''){
        displayError("stateId", "Please select State")
    }
     if (document.getElementById("cityId").value == ''){
        displayError("cityId", "Please select City")
    }
     if (document.getElementById("nationality").value == ''){
        displayError("nationality", "Please enter Nationality")
    }
     if (document.getElementById("Pincode").value == ''){
        displayError("Pincode", "Please enter Pin Code")
    }
     if (document.getElementById("counselor_name").value == ''){
        displayError("counselor_name", "Please enter Counselor Name")
    }
   
    if (type == 'add' || type == 'add_others'){
     if (document.getElementById('secondary_year').value != '' || document.getElementById('secondary_board').value != '' || document.getElementById('secondary_percentage').value != ''){
      
        if (document.getElementById('secondary_document').value == ''){
            console.log('secondary_document', document.getElementById('secondary_document').value)
            displayError('secondary_document', 'Please upload document for Secondary/High School Level');
        }
    }
     if (document.getElementById('sr_year').value != '' || document.getElementById('sr_board').value != '' || document.getElementById('sr_percentage').value != ''){
        if (document.getElementById('sr_document').value == ''){
            displayError('sr_document', 'Please upload document for Sr. Secondary');
        }
    }
     if (document.getElementById('under_year').value != '' || document.getElementById('under_board').value != '' || document.getElementById('under_percentage').value != ''){
        if (document.getElementById('under_document').value == ''){
            displayError('under_document', 'Please upload document for Under Graduation');
        }
    }
     if (document.getElementById('post_year').value != '' || document.getElementById('post_board').value != '' || document.getElementById('post_percentage').value != ''){
        if (document.getElementById('post_document').value == ''){
            displayError('post_document', 'Please upload document for Post Graduation');
        }
    }
     if (document.getElementById('mphil_year').value != '' || document.getElementById('mphil_board').value != '' || document.getElementById('mphil_percentage').value != ''){
        if (document.getElementById('mphil_document').value == ''){
            displayError('mphil_document', 'Please upload document for Eng. Diploma / ITI');
        }
    }
}
if (type == 'edit' || type == 'edit_others'){
    if (document.getElementById('secondary_year').value != '' || document.getElementById('secondary_board').value != '' || document.getElementById('secondary_percentage').value != ''){
      
        if (document.getElementById('uploaded-doc-secondary').value == 'No documents chosen'){
            console.log('secondary_document', document.getElementById('secondary_document').value)
            displayError('secondary_document', 'Please upload document for Secondary/High School Level');
        }
    }
     if (document.getElementById('sr_year').value != '' || document.getElementById('sr_board').value != '' || document.getElementById('sr_percentage').value != ''){
        if (document.getElementById('uploaded-doc-sr').value == ''){
            displayError('sr_document', 'Please upload document for Sr. Secondary');
        }
    }
     if (document.getElementById('under_year').value != '' || document.getElementById('under_board').value != '' || document.getElementById('under_percentage').value != ''){
        if (document.getElementById('uploaded-doc-under').value == ''){
            displayError('under_document', 'Please upload document for Under Graduation');
        }
    }
     if (document.getElementById('post_year').value != '' || document.getElementById('post_board').value != '' || document.getElementById('post_percentage').value != ''){
        if (document.getElementById('uploaded-doc-post').value == ''){
            displayError('post_document', 'Please upload document for Post Graduation');
        }
    }
     if (document.getElementById('mphil_year').value != '' || document.getElementById('mphil_board').value != '' || document.getElementById('mphil_percentage').value != ''){
        if (document.getElementById('uploaded-doc-mphil').value == ''){
            displayError('mphil_document', 'Please upload document for Eng. Diploma / ITI');
        }
    }
}
if (type !== 'add_others' && type !== 'edit_others'){

   
     if (document.getElementById('session').value == ''){  
        displayError('session', 'Please select Session');
    }
     if (document.getElementById('studypattern').value == ''){  
        displayError('studypattern', 'Please select Study Pattern');
    }
     if (document.getElementById('entry_mode').value == ''){  
        displayError('entry_mode', 'Please select Admission Mode');
    }
     if (document.getElementById('course').value == ''){  
        displayError('course', 'Please select Course');
    }
    if (document.getElementById('Stream').value == ''){  
        displayError('Stream', 'Please select Stream');
    }
  
     if (document.getElementById('semyear').value == ''){  
        displayError('semyear', 'Please select Semester/Year');
    }
    if (document.getElementById('fees').value == ''){  
        displayError('fees', 'Please enter Amount');
    }

}
    
   
   
     if (document.getElementById('fees_reciept').value == ''){  
        displayError('fees_reciept', 'Please select Fees Receipt');
    }
     
     if (document.getElementById('date_of_transaction').value == ''){  
        displayError('date_of_transaction', 'Please enter Transaction Date');
    }
     if (document.getElementById('payment_mode').value == ''){  
        displayError('payment_mode', 'Please select Payment Mode');
    }
     if (document.getElementById('remarks').value == ''){  
        displayError('remarks', 'Please enter Remarks');
    }
    if (type == 'add' || type == 'add_others') {
    if (document.getElementById("no_of_documents").value > 0){
        var document_counter = document.getElementById("no_of_documents").value;
        for (i = 1; i <= document_counter; i++){
            
            let idname = `DocumentFront${i}`;
           
            let temp =document.getElementById(`${idname}`).value
            if (temp == "")
                displayError(`${idname}`, "Please upload Front Document")
           
        }
        
      
    }
}
   
        if (error_counter != 0){
            $('#student_save_button').removeAttr('disabled');
            $('#exampleModal').modal('show');
        }
        else{
            if (type == 'add') 
                save_student_form.submit();
            if (type == 'add_others') 
                save_others_student_form.submit();
            if (type == 'edit' || type == 'edit_others')
                return true;
            
        }
    }
 




function checkType(abc, counter){
    let selectedOption = abc.value;
  
                    if (selectedOption === 'Other') {
                        // Show the popup
                        $(`#popupInput${counter}`).removeClass('d-none');
                        $(`#popupInput${counter}`).addClass('d-block');
                    
                    } else {
                        // Hide the popup if another option is selected
                        $(`#popupInput${counter}`).addClass('d-none');
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

function showAlternate(option) {
        
    var temp = `${option}div`;
    document.getElementById(temp).classList.remove("d-none");
    document.getElementById(temp).classList.add("d-block");
}

function calculateDues(){
    var total = document.getElementById('total_fees').value;
    var paid = document.getElementById('fees').value;
    due = parseFloat(total) - parseFloat(paid);
    document.getElementById('dues').value = due;
}

function validateEmail(email) {
    //alert("hhh")
    var re = /\S+@\S+\.\S+/;
    //alert(re.test(email))
    return re.test(email);
}