<?xml version="1.0" encoding="UTF-8" ?>
<Package name="Feedback" format_version="4">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="behavior_1" xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs>
        <Dialog name="feedback" src="feedback/feedback.dlg" />
    </Dialogs>
    <Resources>
        <File name="pepper" src="html/css/pepper.css" />
        <File name="logo" src="html/images/logo.png" />
        <File name="index" src="html/index.html" />
        <File name="jquery-2.1.4.min" src="html/js/jquery-2.1.4.min.js" />
        <File name="main" src="html/js/main.js" />
        <File name="qimessaging_helper" src="html/js/qimessaging_helper.js" />
        <File name="main" src="main.py" />
        <File name="customerquery" src="customerquery.py" />
    </Resources>
    <Topics>
        <Topic name="feedback_enu" src="feedback/feedback_enu.top" topicName="feedback" language="en_US" />
    </Topics>
    <IgnoredPaths />
    <Translations auto-fill="en_US">
        <Translation name="translation_en_US" src="translations/translation_en_US.ts" language="en_US" />
    </Translations>
</Package>
