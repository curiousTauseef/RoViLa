
# RoViLa: Robot-Vision-Language

This repository contains ROS packages that are needed to operate the Mico robot arm developed by Kinova.  The implemented system can be used as a base for extension and implementation of functionalities for the robot arm.

This README contains an overview of the recommended skills paired with useful tutorials/wiki-pages/github repo's that can prove useful to read before working with the nodes in this repository. Subsequently an overview of the implemented system is given and the functionalities of this system are discussed. 

Before doing any further work on this project, it is recommended to have a look at the [Prerequisites](#recommended-skills) section. It is also advisable that any further work done on this repository is implemented and tested on the desktop that already contains this project instead of reinstalling the project on another computer. However, to facilitate reinstalation, a seperate markdown file is included that addresses the different components that have to be installed in case a [full (re)install](INSTALL.md) is needed. 

## Prerequisites
* Python2.7 --> ROS  does not support python3 in kinetic
* Linux (Ubuntu 16.04)
* ROS (Kinetic): [tutorials](http://wiki.ros.org/ROS/Tutorials)

## Cloning this repository
See [(re)install-instructions](INSTALL.md) to verify that you have everything in case you plan on doing a reinstall.

If that is the case or if you want a fresh copy on an already configured system, this repository can be cloned as follows:

```bash
git clone --recurse-submodules https://github.com/ML-KULeuven/RoViLa
```

This will also clone the kinova-ros and iai_kinect2 packages.
After cloning the repository and its submodules, you need to move the folders provided in the [dependencies directory](dependencies/) to the correct directories in the submodules.

The [dependencies/data/502039243042](dependencies/data/502039243042/) directory contains calibration files for the used kinect2 camera. (note if you are using another kinect2 camera these files might not work because calibration is camera-specific). It should be moved to the data directory under the kinect2_bridge package.

The [dependencies/m1n6s200_moveit_config](dependencies/m1n6s200_moveit_config/) directory contains configuration files that have been made with the moveit setup assistant specifically for the robot in use (Mico 1 6DOF 2 fingers). It should be moved to the robot_configs directory under the kinova_moveit package.

```bash
cd ~/RoViLa
cp -r dependencies/data/502039243042 src/iai_kinect2/kinect2_bridge/data/
cp -r dependencies/m1n6s200_moveit_config/ src/kinova-ros/kinova_moveit/robot_configs/
```

Subsequently add the .rules files from the kinova-ros package to the rules.d directory on your system to be able to access the robot arm via usb:

```bash
sudo cp kinova_driver/udev/10-kinova-arm.rules /etc/udev/rules.d/
```

If the instructions from the reinstall page have been followed or if you simply want a fresh copy of this repository on an already configured system, you should now be able to use catkin_make to build the RoViLa workspace:

```bash
cd ~/RoViLa
catkin_make
```

Don't forget to source the workspace:
```bash
source ~/RoViLa/devel/setup.bash
```

You should now be able to test the iai_kinect2 package as follows:

* Connect the kinect2 camera and run the kinect2_bridge node:
```bash
roslaunch kinect2_bridge kinect2_bridge.launch
```

* View the results with:
```bash
rosrun kinect2_viewer kinect2_viewer kinect2 sd cloud
```

You should see the following:
<figure align="center">
	<img src="images/Kinect2_bridge.png?raw=true" alt="kinect2_bridge"/>
</figure>

You should also be able to test the kinova-ros package with the actual robot by executing the following:

* Restart the robot
* Launch the kinova_bringup node for the used robot (in this case m1n6s200):
```bash
roslaunch kinova_bringup kinova_robot.launch kinova_robotType:=m1n6s200
```

This should open the fingers on the robot
You should then be able to call the following command to home the robot (from another terminal):
```bash
 rosservice call /m1n6s200_driver/in/home_arm
 ```

And the arm should move to its home position.
<figure align="center">
	<img src="images/robot_arm_positions.jpg?raw=true" alt="Rest and Home positions of robot arm" style="width:100%"/>
</figure>


## Running the system
To run the entire system, plug in the kinect camera (USB 3.0!) and the Mico arm. Then turn on the Mico arm and execute the following steps:

* Open a terminal and run kinova_bringup to launch the drivers for the Mico arm (m1n6s200):
```bash
roslaunch kinova_bringup kinova_bringup.launch kinova_robotType:=m1n6s200
```

* Open a new terminal window and run the observer node, this node will launch the kinect2_bridge node. WARNING: This node is prone to error if the camera cannot clearly see ar_marker_1. If an error is shown that says that there are unconnected trees, kill the observer node and start it again.
```bash
roslaunch observer_node observer_node.launch
```

* Open another terminal and start the custom moveit configuration for the Mico robot arm, this will also start the rviz plugin that can be used to display trajectories and to do simulations with the robot even if it is not connected (in that case use m1n6s200_virtual_robot.launch):
```bash
roslaunch m1n6s200_moveit_config m1n6s200_demo.launch
```

* Open a fourth terminal and start the actuator node that will home the robot arm and then move it to the starting position:
```bash
roslaunch actuator_node actuator_node.launch
```

* Open one last terminal and wait till the robot is in its starting position, then execute the following command to record speech input and in the end give a command to the robot arm:
```bash
roslaunch main_node main_process.launch
```

## High-level overview of the system
<figure align="center">
	<img src="images/Overview_ROS.png?raw=true" alt="Overview ROS"/>
</figure>


Shown in this figure are the two main subcomponents of this project: [<i>Speech-To-Logic-Form</i>](#speech-to-logic-form) and [<i>Logic-Form-To-Robot-Action</i>](#logic-form-to-robot-action). The first will retrieve speech input and parse it to logic form by using a pre-trained parser. The second will take this parsed string as input and use observations of the world around the robot to execute the action expressed in the logic form.

## Speech-To-Logic-Form
The purpose of this component is transforming speech, input through a microphone, to a logical format that can be processed easily by the <i>Logic-Form-To-Robot-Action</i> component. 

You can run this component by executing the following command in terminal:

```bash
roslaunch main_node main_process.launch
```

The [main_process.launch file](src/main_node/launch/main_process.launch) contains the ROS nodes that need to be started when the above command is executed. This launch file will launch the following ROS nodes (in order): the <i>main\_node</i>, the <i>speech\_node</i>, the <i>speech\_recognizer\_node</i> and finally the <i>parser\_node</i>.

### main_node

This ROS package contains the main node that will be running constantly while the <i>Speech-To-Logic-Form</i> component is being executed. The purpose of this node is to facilitate communication between nodes. Therefore <i>main\_node</i> will act as a middleman that requests services provided by the other 3 components. Finally, once the services provided by the <i>speech\_node</i>, <i>speech\_recognizer\_node</i> and <i>parser\_node</i> have been called, the main node will publish the parsed logic form as a String on the ```/actuation_command``` topic.

### speech_node

The speech\_node ROS package provides the <i>SpeechStream</i> service to the main node. At the start of the system the main node will request input from the speech service. The speech service will record what the user says and parse this recording into a string array.

```bash
 # request fields
int64 chunk_size
int64 sample_format
int64 channels
int64 frequency
int64 seconds
---
 # response fields
string[] stream
```
 
This ROS package uses the PyAudio python streaming library, to enable speech input from python code.  This library also ensures reliable parsing of the given speech input If this package is not yet installed on your system use the following:
```bash
python2.7 -m pip install pyaudio
```
If the above install failse with an error:  <b>Failed building wheel for pyaudio</b>.
Then install the following packages and try again, this should solve the issue.
```bash
sudo apt install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg libav-tools
python2.7 -m pip install pyaudio
```

The launch file of the main node contains parameters that specity the information that is needed to make python receive input from your microphone.

### speech_recognizer_node

The speech\_recognizer\_node ROS package provides the <i>AudioToText</i> service to the main node

```bash
 # request fields
string[] frames
int64 channels
int64 sample_format
int64 frequency
---
 # response fields
string text
```

This ROS package first transforms the stream of frames to a WAV audio file with pyaudio. Then, this node will use PocketSphinx to tansform a stream of frames to a String. Pocketsphinx is a python library for speech recognition which is a subset of CMUSphinx. It can be installed as follows:

```bash
sudo apt-get install -y python python-dev python-pip build-essential swig git libpulse-dev libasound2-dev
python2.7 -m pip install pocketsphinx
```

Pocketsphinx comes with its own vocabulary, dictionary and language models. To avoid the language models giving back sentences that do not correspond with what was said, I have provided a custom corpus, dictionary and LM included in the [data directory](src/speech_recognizer_node/data) of the speech_recognizer_node. The sentences in the [corpus](src/speech_recognizer_node/data/corpus.txt) show possible commands that can be given to the system. This can be extended to include other commands like for example: <i> Put the red cube between the blue cube and the yellow cube</i>. However, when sentences are added to the corpus, the dictionary and language model files have to be re-generated. The [lmtool](http://speech.cs.cmu.edu/tools/lmtool-new.html) from the CMUSPhinx webpage can be used for this. Once the files have been generated, a zip file can be downloaded and the new LM and dictionary can be copied to the data directory replacing the old ones. (You will either have to rename dictionary and LM files to match the names of the old ones or change the paths provided in the [recognizer.py script](src/speech_recognizer_node/scripts/recognizer.py).




### parser_node
 
The parser\_node ROS package provides the <i>ParseTextToLogicForm</i> service to the main node.

```bash
 # request fields
string text
---
 # response fields
string parsed
```

This ROS package is based on a logical parser developed by Pieter-Jan Coenen. I made small adjustments to his code to be able to make a runnable jar file that could in turn be executed from a python script. I chose to do this instead of using ROSJava (a ROS workspace environment for Java), because incorporating ROSJava with the normal ROS installation was non-trivial. The code Pieter-Jan wrote, along with the small adjustments I made can be found in the following repository: [GenLex](https://github.com/ML-KULeuven/GenLex). The jar file has already been made and is included in the [scripts/jar](src/parser_node/scripts/jar/) directory of the parser node as well as a folder containing different trained vectors.

To be able to execute the [parsing.py](src/parser_node/scripts/parsing.py) script, openjdk-8 must be installed:
```bash
sudo apt-get install openjdk-8-jdk
```

To check if the jar executes correctly you can run the following command in the scripts/jar directory of the parser_node:
```bash
cd ~/RoViLa/src/parser_node/scripts/jar/
java -jar parsing.jar trained_vectors/trained_fold_0 "Put the blue cube on the red cube."
```
The output should be:
Put(On(Blue(Block(null)), Red(Block(null))))

When the parser_node is called by the main node, the string recognized by pocketsphinx from the speech input, is provided. This string is parsed using the default <i>trained_fold_0</i> weights.

## Logic-Form-To-Robot-Action
Once the main node gets a response from the parser node containing the parsed string, it calls the actuator node. The actuater_node package will call the observation_node package to get the observations that the camera currently sees to then deduce whether the given command can be executed by the robot arm.

### observer_node

The observer_node package uses the kinect2_bridge ROS interface to provide real-time observations of the current environment surrounding the robot. Periodically it will make an observation of the ar_markers that are currently surrounding the robot, transform the coordinates of those markers to a coordinate with respect to the base of the robot, and send these observations to the actuator node.

To be able to transform coordinates to different frames, the [tf2](http://wiki.ros.org/tf2) library as well as the [tf2_ros](http://wiki.ros.org/tf2_ros) package that provides bindings for Python. If these packages are not yet installed, execute the following command:
```bash
sudo apt-get install ros-kinetic-tf2 ros-kinetic-tf2-ros ros-kinetic-tf2-tools ros-kinetic-tf
```

To be able to transform the location of the ar tag with respect to the camera to a coordinate in the frame that has the robot arm as its origin, ar marker 1 is attached to the robot base.

<figure align="center">
	<img src="images/robot_base_ar_marker_1.JPG?raw=true" alt="ar_marker_1 on robot base" style="width:50%"/>
</figure>

This marker is as a reference to the location of the robot and a static transformation is provided in the launch file of the observer node that transforms ar_marker_1 to the actual origin of the robot:
```xml
<node pkg="tf2_ros" type="static_transform_publisher" name="kinova_base_link_broadcaster" args="-0.0575 0.0275 0.047 0 0 0 ar_marker_1 m1n6s200_link_base" />
```

More information is provided in the [observer_node.launch](src/observer_node/launch/observer_node.launch) file.

### actuator_node

The actuator\_node ROS package contains the actuation component that will send commands to the robot through a [moveit configuration](dependencies/m1n6s200_moveit_config/launch/m1n6s200_demo.launch) which was constructed specifically for the Mico robot arm. This configuration was made using the [MoveIt! setup assistant](http://docs.ros.org/kinetic/api/moveit_tutorials/html/doc/setup_assistant/setup_assistant_tutorial.html) and is based on the configurations of other robots that are by default provided in the kinova-ros package.

When launched, the actuator_node will send the robot to it's initial position. 
<figure align="center">
	<img src="images/robot_arm_start_position.JPG?raw=true" alt="ar_marker_1 on robot base" style="width:50%"/>
</figure>

After receiving the command from the main node, the actuator will deduce the action that it needs to do. Currently the only supported action is picking up a block and putting it on another block. For example:
Put the red block on the blue block.

Once the actuator has deduced the action as well as the blockes involved in the action, it will wait till it receives a message from the observer node on the <i>/observations</i> topic. In this message it will look for the ar tags that the blocks in question contain. If these ar tags are present, the moveit is called to plan a trajectory to the position of one of the ar tags. If moveit finds a trajectory, the action is executed by the robot.

## Built With

* [ROS](http://www.ros.org/) - The Robot operating system
* [Catkin](https://www.wiki.ros.org/catkin) - Dependency Management and building nodes
* [Kinova-ROS](https://github.com/Kinovarobotics/kinova-ros) - ROS nodes that facilitate use of Kinova robot arms
* [iai_kinect2](https://github.com/code-iai/iai_kinect2) - Incorporating the kinect2 camera in the Robot Operating System

## Authors

* **Shani Vanlerberghe**

## Contributors
* **Shani Vanlerberghe**
* **Pedro Zuidberg Dos Martires**
* **Wannes Meert**
* **Luc De Raedt**

## Acknowledgments
* **Pieter-Jan Coenen** - *The text to logic form parser*
