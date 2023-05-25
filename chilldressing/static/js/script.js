// some scripts

// jquery ready start
$(document).ready(function () {
    // jQuery code


    /* ///////////////////////////////////////

    THESE FOLLOWING SCRIPTS ONLY FOR BASIC USAGE, 
    For sliders, interactions and other

    */ ///////////////////////////////////////


    //////////////////////// Prevent closing from click inside dropdown
    $(document).on('click', '.dropdown-menu', function (e) {
        e.stopPropagation();
    });


    $('.js-check :radio').change(function () {
        var check_attr_name = $(this).attr('name');
        if ($(this).is(':checked')) {
            $('input[name=' + check_attr_name + ']').closest('.js-check').removeClass('active');
            $(this).closest('.js-check').addClass('active');
            // item.find('.radio').find('span').text('Add');

        } else {
            item.removeClass('active');
            // item.find('.radio').find('span').text('Unselect');
        }
    });


    $('.js-check :checkbox').change(function () {
        var check_attr_name = $(this).attr('name');
        if ($(this).is(':checked')) {
            $(this).closest('.js-check').addClass('active');
            // item.find('.radio').find('span').text('Add');
        } else {
            $(this).closest('.js-check').removeClass('active');
            // item.find('.radio').find('span').text('Unselect');
        }
    });



    //////////////////////// Bootstrap tooltip
    if ($('[data-toggle="tooltip"]').length > 0) {  // check if element exists
        $('[data-toggle="tooltip"]').tooltip()
    } // end if





});
// jquery end

setTimeout(function () {
    $('.message').fadeOut('slow')
}, 3000)

function validatePhoneNumber() {
    var phoneNumberInput = document.getElementById("id_phone_number");
    var phoneNumber = phoneNumberInput.value.trim();

    var phoneNumberRegex = /^\+\d{11}$/; // Adjust the regular expression based on your desired phone number format

    if (!phoneNumber.match(phoneNumberRegex)) {
        var phoneErrorElement = document.getElementById("phone-error");
        phoneErrorElement.innerHTML = "Please enter a valid phone number.";

        // Apply fade-out effect
        phoneErrorElement.style.opacity = 1;
        setTimeout(function () {
            fadeOut(phoneErrorElement);
        }, 2000);

        return false;
    }

    document.getElementById("phone-error").innerHTML = ""; // Clear error message
    return true;
}

function fadeOut(element) {
    var opacity = 1;
    var interval = setInterval(function () {
        if (opacity > 0) {
            opacity -= 0.1;
            element.style.opacity = opacity;
        } else {
            clearInterval(interval);
            element.style.opacity = 0;
            element.innerHTML = ""; // Clear error message after fade-out
        }
    }, 100);
}

