# Primer Document: ESIM
This documents the event camera simulator we will be using in this project: [ESIM](https://github.com/uzh-rpg/rpg_esim).

## Required Background Knowledge
### ROS
Using ESIM requires basic knowledge of ROS. To install ROS, click [here](http://wiki.ros.org/ROS/Installation). 

After installing ROS, follow the basic ROS tutorials [here](http://wiki.ros.org/ROS/Tutorials), specifically [Understanding ROS Nodes](http://wiki.ros.org/ROS/Tutorials/UnderstandingNodes) and [Understanding ROS Topics](http://wiki.ros.org/ROS/Tutorials/UnderstandingTopics).

**Note**: When setting up your ROS, it is important to use ``` catkin build ``` as opposed to ``` catkin_make ``` from the catkin_tools. ``` catkin build ```is more compartmentalized and robust to changes in workspace. Read more about the difference between ``` catkin build ``` and ``` catkin_make ``` or migrating from ``` catkin_make ``` to ``` catkin build ``` [here](https://catkin-tools.readthedocs.io/en/latest/migration.html).


## Generate SSH Key and Link to Github Account
SSH key must be linked to your Github account to succcessfully install the simulation. Generate your key by folliwng the Github tutorial [here](https://help.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) and upload it to your Github account [here](https://help.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account).

If you already have a SSH key linked to your Github account, you may proceed directly to the **Installation** section. 

## Installation
The installation instructions for the ESIM simulatorm is [here](https://github.com/uzh-rpg/rpg_esim/wiki/Installation).

## Simulating Events from a Video
This [tutorial](https://github.com/uzh-rpg/rpg_esim/wiki/Simulating-events-from-a-video) shows how to use ESIM to simulate events from a given video.  Individual frames from the input video (may include motion blur) will be extracted. ESIM will use the frames from the input video to simulate events and these simulated events are visualized in the ```dvs_renderer``` node.

**Note**: If you have problems using ```youtube-dl``` in the tutorial, install ```youtube-dl``` from the default repositories in all currently supported versions of Ubuntu with this command instead:
```sudo apt install youtube-dl```

### Warning
**This will not work for any video**. The video needs to have a sufficiently **high framerate**: the pixel displacement between successive images needs to be small (i.e. a few pixels at most). Otherwise, the simulated events will be in poor quality.

## Test Installation with Planar Renderer
Check if you've successfully installed ESIM by going through the tutorials of [Planar Renderer](https://github.com/uzh-rpg/rpg_esim/wiki/Planar-Renderer). Planar Renderer simulates a 3D camera motion in a planar scene (one plane with texture attached to it).

To edit sensor parameters (e.g., camera, IMU), edit the ``` cfg/example.conf ``` file.
