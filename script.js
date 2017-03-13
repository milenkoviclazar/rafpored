function changeCalendar() {
    var mainSrc = "https://calendar.google.com/calendar/embed?showTitle=0&mode=WEEK&height=600&wkst=2&bgcolor=%23ffffff&src=rafpored%40gmail.com&color=%231B887A&ctz=Europe%2FBelgrade";
    var checkboxes = document.getElementsByName('chkbx');
    for (var i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked) {
            mainSrc += "&src=" + checkboxes[i].value + "&color=%238C500B";
        }
    }
    document.getElementById("calendarFrame").src = mainSrc;
}