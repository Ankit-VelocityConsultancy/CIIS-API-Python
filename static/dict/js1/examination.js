<<<<<<< HEAD
function saveExam(){
    console.log(" Exam Submitted");
    var radioValue1 = $("input[name='radio_option_1']:checked").val();
    if(radioValue1){
        console.log(radioValue1);
    }
    var radioValue2 = $("input[name='radio_option_2']:checked").val();
    if(radioValue2){
        console.log(radioValue2);
    }

    // var data = new FormData();
    // var formData = $('#my_form').serializeArray();
    // data.append('exam_data',formData);
    // console.log(data)
    // var a = $("my_form").serialize();
    // console.log(a);
    


    // $.ajax({ // create an AJAX call...
    //     type: "POST",
    //     url: "https://erp.ciisindia.in/exam/",
    //     headers: {'X-CSRFToken': '{{ csrf_token }}'},
    //     data: {
    //         'show':'yes'
    //     },
    //     success: function(response) {
    //         console.log("exam data sent to views")
    //     }
    // });
=======
function saveExam(){
    console.log(" Exam Submitted");
    var radioValue1 = $("input[name='radio_option_1']:checked").val();
    if(radioValue1){
        console.log(radioValue1);
    }
    var radioValue2 = $("input[name='radio_option_2']:checked").val();
    if(radioValue2){
        console.log(radioValue2);
    }

    // var data = new FormData();
    // var formData = $('#my_form').serializeArray();
    // data.append('exam_data',formData);
    // console.log(data)
    // var a = $("my_form").serialize();
    // console.log(a);
    


    // $.ajax({ // create an AJAX call...
    //     type: "POST",
    //     url: "https://erp.ciisindia.in/exam/",
    //     headers: {'X-CSRFToken': '{{ csrf_token }}'},
    //     data: {
    //         'show':'yes'
    //     },
    //     success: function(response) {
    //         console.log("exam data sent to views")
    //     }
    // });
>>>>>>> 0afb1a7cdc5b133066f85bb3be6fd7c58409a049
}