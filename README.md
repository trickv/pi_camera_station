# pi_camera_station

The goal of this project is to build a camera which can take pictures anywhere in the world without relying on any fixed power or wifi connections, for deployment on Madeline Island to try and get a few photos year 'round in a place where almost no one goes.

This is a mess of code to run on the Pi which has:
- Pi (zero, but an A will do) powered by a LiPo battery + tp4056 solar charging circuit and 2.5W allpower solar panel
- sim7080g LTE CAT-M1 / NB-IoT modem; original design was a sim800g
- relay to allow slow startup of the sim7080g
- hard switch to allow turning the wifi off via rfkill

This posts pictures to a server of mine - you won't want to use my server. But if you dig into my other related code repositories you can see the code that runs server side, and set your own up.

Related code:
- https://github.com/trickv/pi_camera_watch_ui
- TODO: import hacks.v9n.us API endpoint
