After following VINS installation steps:
```sudo apt-get install python-catkin-tools python-vcstool```

Then go to src/wxyz/VINS-Mono, then
```vcs-import < dependencies.yaml```


Terminal 1

```roslaunch vins_estimator dvs.launch```

Terminal 2

```roslaunch vins_estimator vins_rviz.launch```

Terminal 3

```roslaunch /VINS-Mono/launch/event.launch ```




