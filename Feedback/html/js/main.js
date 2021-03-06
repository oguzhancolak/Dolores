function surveyClicked(value) {
    if (value != "G")
        $("#record").removeClass("hidden");
    session.raiseEvent("Feedback/SurveyClicked", value);
    setTimeout(exitWoRecord,6000);

}

$(document).ready(function () {

    session.subscribeToEvent("Feedback/SetRecordDuration", setDuration);
    session.subscribeToEvent("Feedback/StartTimeout", startTimer);
});

var micState = 'off';
var timeOutId;
var recordDuration;

function setDuration(val) {
    recordDuration = parseInt(val) * 1000;
}

function exitWoRecord()
{
    if(micState == 'off')
    {
        exit();
    }
}

function micClicked() {
    if (micState == 'off') {
        micState = 'on';
        $("#record").addClass("active");
        $("#warning").css("visibility", "visible");
        timeOutId = setTimeout("micClicked()", recordDuration);
        session.raiseEvent("Feedback/ProcessRecording", "S");
    } else {
        clearTimeout(timeOutId);
        micState = 'off';

        $("#record").removeClass("active");
        $("#warning").css("visibility", "hidden");
        session.raiseEvent("Feedback/ProcessRecording", "E");
    }

}

function exit() {
    session.raiseEvent("Feedback/NoAction", 1);
}

var checked = 1;
var timeout = 5000;

function startTimer(value) {
    checked = value;
    setTimeout(checkForInput, timeout);
}



var checkForInput = function () {
    if (checked == 1)
        session.raiseEvent("Feedback/CheckForAction", "reminder");
    else if (checked == 2)
        session.raiseEvent("Feedback/CheckForAction", "endit");
}

