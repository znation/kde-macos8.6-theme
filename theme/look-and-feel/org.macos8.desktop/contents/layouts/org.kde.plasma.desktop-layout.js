// Mac OS 8.6 menu bar: one flush 20px panel across the top of the screen.
// Reference desktop_betawiki.png at x=300 and x=400: row 0 #FFFFFF, rows
// 1-17 #DDDDDD, row 18 #999999, row 19 #000000, then the desktop pattern.
var panel = new Panel;
panel.location = "top";
panel.height = 20;
panel.floating = false;

panel.addWidget("org.kde.plasma.kicker");
panel.addWidget("org.kde.plasma.appmenu");
panel.addWidget("org.kde.plasma.panelspacer");
panel.addWidget("org.kde.plasma.systemtray");
// Reference desktop_betawiki.png x=882..925: "5:01 PM", 12-hour with AM/PM,
// no seconds, no date. Known limit: the clock has no setting for a leading
// zero on the hour; that comes from the locale's time format.
var clock = panel.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", false);
clock.writeConfig("showSeconds", 0);
clock.writeConfig("use24hFormat", 0);
panel.addWidget("org.kde.plasma.windowlist");

var desktopsArray = desktopsForActivity(currentActivity());
for (var j = 0; j < desktopsArray.length; j++) {
    desktopsArray[j].wallpaperPlugin = 'org.kde.image';
}
