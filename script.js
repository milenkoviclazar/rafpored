var colors = ['A32929', 'B1365F', '7A367A', '5229A3', '29527A', '2952A3', '1B887A',
    '28754E', '0D7813', '528800', '88880E', 'AB8B00', 'BE6D00', 'B1440E',
    '865A5A', '705770', '4E5D6C', '5A6986', '4A716C', '6E6E41', '8D6F47',
    '853104', '691426', '5C1158', '23164E', '182C57', '060D5E', '125A12',
    '2F6213', '2F6309', '5F6B02', '875509', '8C500B', '754916', '6B3304',
    '5B123B', '42104A', '113F47', '333333', '0F4B38', '856508', '711616'];

function changeCalendar() {
    var mainSrc = "https://calendar.google.com/calendar/embed?showTitle=0&mode=WEEK&height=600&wkst=2&bgcolor=%23ffffff&src=rafpored%40gmail.com&color=%231B887A&ctz=Europe%2FBelgrade";
    var checkboxes = document.getElementsByName('chkbx');
    for (var i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked) {
            console.log("&color=%23" + colors[i % colors.length]);
            mainSrc += "&src=" + checkboxes[i].value + "&color=%23" + colors[i % colors.length];
        }
    }
    document.getElementById("calendarFrame").src = mainSrc;
}