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
    // Reference desktop_betawiki.png: icons fill one 32px column (x=960..991)
    // at the right edge, top down (arrangement 1 = columns, alignment 1 =
    // right, iconSize 1 = 32px); nothing differs from the wallpaper at x<880.
    desktopsArray[j].currentConfigGroup = ["General"];
    desktopsArray[j].writeConfig("arrangement", 1);
    desktopsArray[j].writeConfig("alignment", 1);
    desktopsArray[j].writeConfig("iconSize", 1);
    // Each icon block is a 32-row body plus one 13-row label line (the first
    // block measures 44 rows, the rest 45); textLines 1 keeps the label to one line.
    desktopsArray[j].writeConfig("textLines", 1);
}
